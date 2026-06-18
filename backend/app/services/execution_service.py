import asyncio
import time
import traceback
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.workflow import Workflow, WorkflowTask, WorkflowEdge
from app.models.execution import WorkflowRun, TaskExecution, RunStatus, TaskStatus
from app.services.workflow_service import get_workflow


async def execute_workflow(db: AsyncSession, workflow_id: str, triggered_by: str = "manual") -> WorkflowRun:
    wf = await get_workflow(db, workflow_id)
    if not wf:
        raise ValueError(f"Workflow {workflow_id} not found")

    run = WorkflowRun(
        workflow_id=workflow_id,
        status=RunStatus.RUNNING,
        triggered_by=triggered_by,
        started_at=datetime.now(timezone.utc),
    )
    db.add(run)
    await db.flush()

    task_map = {t.id: t for t in wf.tasks}
    edges_by_target: dict[str, list[str]] = {}
    for e in wf.edges:
        edges_by_target.setdefault(e.target_task_id, []).append(e.source_task_id)

    task_execs = {}
    for t in wf.tasks:
        te = TaskExecution(run_id=run.id, task_id=t.id, status=TaskStatus.PENDING)
        db.add(te)
        await db.flush()
        task_execs[t.id] = te

    await db.commit()

    try:
        await _run_dag(db, run, task_map, edges_by_target, task_execs)
    except Exception as e:
        run.status = RunStatus.FAILED
        run.error_message = str(e)

    run.finished_at = datetime.now(timezone.utc)
    if run.total_duration_ms is None:
        run.total_duration_ms = (run.finished_at - run.started_at).total_seconds() * 1000
    if run.status not in (RunStatus.COMPLETED, RunStatus.FAILED):
        run.status = RunStatus.COMPLETED if not run.error_message else RunStatus.FAILED

    await db.commit()
    await db.refresh(run, ["task_executions"])
    return run


async def _run_dag(
    db: AsyncSession,
    run: WorkflowRun,
    task_map: dict[str, WorkflowTask],
    edges_by_target: dict[str, list[str]],
    task_execs: dict[str, TaskExecution],
):
    completed = set()
    failed = set()
    in_progress = set()

    all_task_ids = set(task_map.keys())

    async def execute_task(task_id: str):
        if task_id in completed or task_id in failed or task_id in in_progress:
            return
        in_progress.add(task_id)
        te = task_execs[task_id]
        task = task_map[task_id]

        try:
            te.status = TaskStatus.RUNNING
            te.started_at = datetime.now(timezone.utc)
            await db.commit()

            start = time.monotonic()
            result = await _run_task(task)
            duration = (time.monotonic() - start) * 1000

            te.status = TaskStatus.COMPLETED
            te.finished_at = datetime.now(timezone.utc)
            te.duration_ms = duration
            te.result = {"output": str(result)[:1000]} if result else {}
            await db.commit()

            completed.add(task_id)
        except Exception as e:
            te.status = TaskStatus.FAILED
            te.finished_at = datetime.now(timezone.utc)
            te.error_message = str(e)[:2000]
            te.logs = traceback.format_exc()[:5000]
            await db.commit()
            failed.add(task_id)
        finally:
            in_progress.discard(task_id)

    async def get_ready_tasks() -> set[str]:
        ready = set()
        for tid in all_task_ids:
            if tid in completed or tid in failed or tid in in_progress:
                continue
            deps = edges_by_target.get(tid, [])
            if all(d in completed for d in deps):
                ready.add(tid)
        return ready

    while len(completed) + len(failed) < len(all_task_ids):
        ready = await get_ready_tasks()
        if not ready:
            if in_progress:
                await asyncio.sleep(0.05)
                continue
            run.status = RunStatus.FAILED
            run.error_message = "Deadlock detected: no ready tasks but uncompleted tasks remain"
            return

        tasks_to_run = []
        for tid in ready:
            tasks_to_run.append(execute_task(tid))
        await asyncio.gather(*tasks_to_run)

    if failed:
        run.status = RunStatus.FAILED
        run.error_message = f"{len(failed)} task(s) failed"


async def _run_task(task: WorkflowTask) -> any:
    task_type = task.task_type
    config = task.config or {}

    if task_type == "python":
        code = config.get("code", "")
        if not code:
            return "no code"
        local_vars = {}
        exec(code, {"__builtins__": __builtins__}, local_vars)
        result = local_vars.get("result", local_vars.get("output", "executed"))
        return result

    elif task_type == "http":
        import httpx
        method = config.get("method", "GET")
        url = config["url"]
        headers = config.get("headers", {})
        body = config.get("body")
        async with httpx.AsyncClient() as client:
            resp = await client.request(method, url, headers=headers, json=body, timeout=30)
            resp.raise_for_status()
            return resp.text[:5000]

    elif task_type == "file":
        import aiofiles
        path = config["path"]
        mode = config.get("mode", "r")
        content = config.get("content", "")
        if "w" in mode or "a" in mode:
            async with aiofiles.open(path, mode) as f:
                await f.write(content)
            return f"wrote {len(content)} bytes to {path}"
        else:
            async with aiofiles.open(path, mode) as f:
                return await f.read()

    elif task_type == "simulate":
        import random
        duration = config.get("simulate_duration_ms", random.randint(100, 2000))
        complexity = config.get("complexity", "medium")
        await asyncio.sleep(duration / 1000)
        return {
            "simulated": True,
            "duration_ms": duration,
            "complexity": complexity,
            "data_size_bytes": random.randint(100, 10000),
        }

    else:
        raise ValueError(f"Unknown task type: {task_type}")
