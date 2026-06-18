import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.workflow import Workflow, WorkflowTask, WorkflowEdge
from app.models.execution import WorkflowRun, TaskExecution, RunStatus
from app.schemas.workflow import WorkflowCreate, WorkflowUpdate


async def create_workflow(db: AsyncSession, user_id: str, data: WorkflowCreate) -> Workflow:
    wf = Workflow(name=data.name, description=data.description, owner_id=user_id)
    db.add(wf)
    await db.flush()

    task_id_map = {}
    for t in data.tasks:
        original_id = t.id
        task = WorkflowTask(
            workflow_id=wf.id,
            name=t.name,
            task_type=t.task_type,
            config=t.config,
            position_x=t.position_x,
            position_y=t.position_y,
        )
        db.add(task)
        await db.flush()
        if original_id:
            task_id_map[original_id] = task.id

    for e in data.edges:
        edge = WorkflowEdge(
            workflow_id=wf.id,
            source_task_id=task_id_map.get(e.source_task_id, e.source_task_id),
            target_task_id=task_id_map.get(e.target_task_id, e.target_task_id),
        )
        db.add(edge)

    await db.refresh(wf)
    return wf


async def get_workflow(db: AsyncSession, workflow_id: str) -> Workflow | None:
    result = await db.execute(
        select(Workflow)
        .options(selectinload(Workflow.tasks), selectinload(Workflow.edges))
        .where(Workflow.id == workflow_id)
    )
    return result.scalar_one_or_none()


async def get_user_workflows(db: AsyncSession, user_id: str) -> list[Workflow]:
    result = await db.execute(
        select(Workflow)
        .options(selectinload(Workflow.tasks))
        .where(Workflow.owner_id == user_id)
        .order_by(Workflow.updated_at.desc())
    )
    return list(result.scalars().all())


async def update_workflow(db: AsyncSession, workflow_id: str, data: WorkflowUpdate) -> Workflow | None:
    wf = await get_workflow(db, workflow_id)
    if not wf:
        return None
    if data.name is not None:
        wf.name = data.name
    if data.description is not None:
        wf.description = data.description
    if data.tasks is not None:
        for existing_task in wf.tasks:
            await db.delete(existing_task)
        for existing_edge in wf.edges:
            await db.delete(db)
        await db.flush()
        task_id_map = {}
        for t in data.tasks:
            task = WorkflowTask(
                workflow_id=wf.id,
                name=t.name,
                task_type=t.task_type,
                config=t.config,
                position_x=t.position_x,
                position_y=t.position_y,
            )
            db.add(task)
            await db.flush()
            task_id_map[t.id or task.id] = task.id
        if data.edges:
            for e in data.edges:
                edge = WorkflowEdge(
                    workflow_id=wf.id,
                    source_task_id=task_id_map.get(e.source_task_id, e.source_task_id),
                    target_task_id=task_id_map.get(e.target_task_id, e.target_task_id),
                )
                db.add(edge)
    wf.version += 1
    await db.refresh(wf)
    return wf


async def delete_workflow(db: AsyncSession, workflow_id: str) -> bool:
    wf = await get_workflow(db, workflow_id)
    if not wf:
        return False
    await db.delete(wf)
    return True


async def get_workflow_runs(db: AsyncSession, workflow_id: str) -> list[WorkflowRun]:
    result = await db.execute(
        select(WorkflowRun)
        .options(selectinload(WorkflowRun.task_executions))
        .where(WorkflowRun.workflow_id == workflow_id)
        .order_by(WorkflowRun.created_at.desc())
    )
    return list(result.scalars().all())


async def get_run(db: AsyncSession, run_id: str) -> WorkflowRun | None:
    result = await db.execute(
        select(WorkflowRun)
        .options(selectinload(WorkflowRun.task_executions))
        .where(WorkflowRun.id == run_id)
    )
    return result.scalar_one_or_none()
