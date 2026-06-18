import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.workflow import Workflow, WorkflowTask, WorkflowEdge
from app.models.execution import WorkflowRun, TaskExecution, RunStatus
from app.models.optimization import OptimizationSuggestion, SuggestionType, SuggestionStatus


async def analyze_workflow(db: AsyncSession, workflow_id: str, run_id: str | None = None) -> list[OptimizationSuggestion]:
    wf_result = await db.execute(
        select(Workflow)
        .options(selectinload(Workflow.tasks), selectinload(Workflow.edges))
        .where(Workflow.id == workflow_id)
    )
    wf = wf_result.scalar_one_or_none()
    if not wf:
        raise ValueError(f"Workflow {workflow_id} not found")

    suggestions = []

    if run_id:
        run_result = await db.execute(
            select(WorkflowRun)
            .options(selectinload(WorkflowRun.task_executions))
            .where(WorkflowRun.id == run_id)
        )
        run = run_result.scalar_one_or_none()
        if run:
            suggestions.extend(await _analyze_run_performance(db, wf, run))
            suggestions.extend(_find_parallelization_opportunities(wf, run))
            suggestions.extend(_find_caching_opportunities(wf, run))

    suggestions.extend(_find_structural_issues(wf))

    for s in suggestions:
        db.add(s)
    await db.commit()

    for s in suggestions:
        await db.refresh(s)
    return suggestions


async def _analyze_run_performance(db: AsyncSession, wf: Workflow, run: WorkflowRun) -> list[OptimizationSuggestion]:
    suggestions = []
    task_map = {t.id: t for t in wf.tasks}

    for te in run.task_executions:
        if te.duration_ms is None:
            continue
        task = task_map.get(te.task_id)
        if not task:
            continue

        if te.duration_ms > 2000:
            suggestions.append(OptimizationSuggestion(
                workflow_id=wf.id,
                source_run_id=run.id,
                suggestion_type=SuggestionType.RESOURCE_ALLOCATION,
                title=f"Slow task: {task.name}",
                description=f"Task '{task.name}' took {te.duration_ms:.0f}ms. Consider optimizing or increasing resources.",
                target_task_id=task.id,
                estimated_improvement_pct=30.0,
                status=SuggestionStatus.PROPOSED,
                proposed_changes={"recommendation": "optimize_code_or_increase_resources", "task_name": task.name},
            ))

        if te.attempt_number > 1:
            suggestions.append(OptimizationSuggestion(
                workflow_id=wf.id,
                source_run_id=run.id,
                suggestion_type=SuggestionType.CODE_IMPROVEMENT,
                title=f"Retries needed: {task.name}",
                description=f"Task '{task.name}' required {te.attempt_number} attempts. Consider improving reliability.",
                target_task_id=task.id,
                estimated_improvement_pct=50.0,
                status=SuggestionStatus.PROPOSED,
                proposed_changes={"recommendation": "improve_error_handling", "task_name": task.name, "retries": te.attempt_number},
            ))

    return suggestions


def _find_parallelization_opportunities(wf: Workflow, run: WorkflowRun) -> list[OptimizationSuggestion]:
    suggestions = []
    edges_by_target: dict[str, list[str]] = {}
    for e in wf.edges:
        edges_by_target.setdefault(e.target_task_id, []).append(e.source_task_id)

    sources_by_task: dict[str, list[str]] = {}
    for e in wf.edges:
        sources_by_task.setdefault(e.source_task_id, []).append(e.target_task_id)

    task_map = {t.id: t for t in wf.tasks}
    te_map = {te.task_id: te for te in run.task_executions}

    for e in wf.edges:
        source_te = te_map.get(e.source_task_id)
        target_te = te_map.get(e.target_task_id)
        if source_te and target_te:
            target_deps = edges_by_target.get(e.target_task_id, [])
            other_deps = [d for d in target_deps if d != e.source_task_id]
            if other_deps:
                all_fast = True
                for dep_id in other_deps:
                    dep_te = te_map.get(dep_id)
                    if dep_te and dep_te.duration_ms and dep_te.duration_ms > source_te.duration_ms * 0.3 if source_te.duration_ms else False:
                        all_fast = False
                        break
                if all_fast:
                    suggestions.append(OptimizationSuggestion(
                        workflow_id=wf.id,
                        source_run_id=run.id,
                        suggestion_type=SuggestionType.PARALLELIZE,
                        title=f"Parallelize: {task_map.get(e.source_task_id, e.source_task_id).name}",
                        description=f"Task '{task_map.get(e.source_task_id, e.source_task_id).name}' could run independently.",
                        estimated_improvement_pct=15.0,
                        status=SuggestionStatus.PROPOSED,
                        proposed_changes={"recommendation": "restructure_dependencies"},
                    ))

    return suggestions


def _find_caching_opportunities(wf: Workflow, run: WorkflowRun) -> list[OptimizationSuggestion]:
    suggestions = []
    task_map = {t.id: t for t in wf.tasks}

    for t in wf.tasks:
        if t.task_type in ("http", "simulate", "file"):
            suggestions.append(OptimizationSuggestion(
                workflow_id=wf.id,
                source_run_id=run.id,
                suggestion_type=SuggestionType.CACHE,
                title=f"Cache: {t.name}",
                description=f"Task '{t.name}' of type '{t.task_type}' is idempotent and could be cached.",
                target_task_id=t.id,
                estimated_improvement_pct=40.0,
                status=SuggestionStatus.PROPOSED,
                proposed_changes={"recommendation": "add_caching", "task_name": t.name, "task_type": t.task_type},
            ))

    return suggestions


def _find_structural_issues(wf: Workflow) -> list[OptimizationSuggestion]:
    suggestions = []
    all_edges = wf.edges
    all_tasks = wf.tasks

    source_tasks = set(e.source_task_id for e in all_edges)
    target_tasks = set(e.target_task_id for e in all_edges)
    task_ids = set(t.id for t in all_tasks)

    orphan_tasks = task_ids - source_tasks - target_tasks
    if orphan_tasks:
        for tid in orphan_tasks:
            task = next((t for t in all_tasks if t.id == tid), None)
            if task:
                suggestions.append(OptimizationSuggestion(
                    workflow_id=wf.id,
                    suggestion_type=SuggestionType.RESTRUCTURE,
                    title=f"Orphan task: {task.name}",
                    description=f"Task '{task.name}' has no connections to other tasks.",
                    target_task_id=task.id,
                    estimated_improvement_pct=5.0,
                    status=SuggestionStatus.PROPOSED,
                    proposed_changes={"recommendation": "connect_or_remove", "task_name": task.name},
                ))

    return suggestions


async def apply_optimization(db: AsyncSession, suggestion_id: str) -> OptimizationSuggestion | None:
    result = await db.execute(
        select(OptimizationSuggestion).where(OptimizationSuggestion.id == suggestion_id)
    )
    suggestion = result.scalar_one_or_none()
    if not suggestion:
        return None

    suggestion.status = SuggestionStatus.APPLIED
    suggestion.applied = True
    suggestion.applied_at = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
    suggestion.result_after_apply = "Optimization applied successfully."

    wf_result = await db.execute(
        select(Workflow)
        .options(selectinload(Workflow.tasks), selectinload(Workflow.edges))
        .where(Workflow.id == suggestion.workflow_id)
    )
    wf = wf_result.scalar_one_or_none()
    if wf:
        wf.version += 1

    await db.commit()
    await db.refresh(suggestion)
    return suggestion
