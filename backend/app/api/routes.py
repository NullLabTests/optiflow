from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.api.deps import get_current_user
from app.models.user import User
from app.models.optimization import OptimizationSuggestion
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.schemas.workflow import (
    WorkflowCreate, WorkflowUpdate, WorkflowResponse, WorkflowListResponse, NLWorkflowRequest,
)
from app.schemas.execution import WorkflowRunResponse, WorkflowRunListResponse
from app.schemas.optimization import (
    OptimizationSuggestionResponse, OptimizationAnalysisRequest, ApplyOptimizationRequest,
)
from app.services.workflow_service import (
    create_workflow, get_workflow, get_user_workflows,
    update_workflow, delete_workflow, get_workflow_runs, get_run,
)
from app.services.execution_service import execute_workflow
from app.services.optimization_service import analyze_workflow, apply_optimization
from app.services.ai_service import generate_workflow_from_nl
from app.services.profiler_service import generate_report

router = APIRouter(prefix="/api/v1")


@router.post("/auth/register", response_model=TokenResponse)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        display_name=data.display_name,
    )
    db.add(user)
    await db.flush()
    token = create_access_token({"sub": user.id})
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))


@router.post("/auth/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.id})
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))


@router.get("/auth/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user)):
    return UserResponse.model_validate(user)


@router.post("/workflows", response_model=WorkflowResponse, status_code=201)
async def create_wf(data: WorkflowCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    wf = await create_workflow(db, user.id, data)
    return WorkflowResponse.model_validate(wf)


@router.get("/workflows", response_model=list[WorkflowListResponse])
async def list_wfs(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    wfs = await get_user_workflows(db, user.id)
    return [
        WorkflowListResponse(
            id=w.id, name=w.name, description=w.description,
            version=w.version, task_count=len(w.tasks),
            created_at=w.created_at, updated_at=w.updated_at,
        )
        for w in wfs
    ]


@router.get("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def get_wf(workflow_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    wf = await get_workflow(db, workflow_id)
    if not wf or wf.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return WorkflowResponse.model_validate(wf)


@router.put("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def update_wf(workflow_id: str, data: WorkflowUpdate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    wf = await update_workflow(db, workflow_id, data)
    if not wf or wf.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return WorkflowResponse.model_validate(wf)


@router.delete("/workflows/{workflow_id}", status_code=204)
async def delete_wf(workflow_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    wf = await get_workflow(db, workflow_id)
    if not wf or wf.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Workflow not found")
    await delete_workflow(db, workflow_id)


@router.post("/workflows/from-nl", response_model=WorkflowResponse, status_code=201)
async def create_wf_from_nl(data: NLWorkflowRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    wf_data = await generate_workflow_from_nl(data.prompt)
    create = WorkflowCreate(
        name=wf_data.get("name", "AI Generated Workflow"),
        description=wf_data.get("description"),
        tasks=[
            {
                "id": t.get("id"),
                "name": t["name"],
                "task_type": t["task_type"],
                "config": t.get("config", {}),
                "position_x": t.get("position_x", 100 + i * 250),
                "position_y": t.get("position_y", 200),
            }
            for i, t in enumerate(wf_data.get("tasks", []))
        ],
        edges=wf_data.get("edges", []),
    )
    wf = await create_workflow(db, user.id, create)
    return WorkflowResponse.model_validate(wf)


@router.post("/workflows/{workflow_id}/execute", response_model=WorkflowRunResponse)
async def execute_wf(workflow_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    wf = await get_workflow(db, workflow_id)
    if not wf or wf.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Workflow not found")
    run = await execute_workflow(db, workflow_id)
    return WorkflowRunResponse.model_validate(run)


@router.get("/workflows/{workflow_id}/runs", response_model=list[WorkflowRunListResponse])
async def list_runs(workflow_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    wf = await get_workflow(db, workflow_id)
    if not wf or wf.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Workflow not found")
    runs = await get_workflow_runs(db, workflow_id)
    return [
        WorkflowRunListResponse(
            id=r.id, workflow_id=r.workflow_id, status=r.status,
            triggered_by=r.triggered_by, started_at=r.started_at,
            finished_at=r.finished_at, total_duration_ms=r.total_duration_ms,
            task_count=len(r.task_executions), created_at=r.created_at,
        )
        for r in runs
    ]


@router.get("/runs/{run_id}", response_model=WorkflowRunResponse)
async def get_run_endpoint(run_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    run = await get_run(db, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    wf = await get_workflow(db, run.workflow_id)
    if not wf or wf.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Run not found")
    return WorkflowRunResponse.model_validate(run)


@router.get("/runs/{run_id}/profile")
async def get_profile(run_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    run = await get_run(db, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    wf = await get_workflow(db, run.workflow_id)
    if not wf or wf.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Run not found")
    report = generate_report(run)
    return report.to_dict()


@router.post("/workflows/{workflow_id}/analyze", response_model=list[OptimizationSuggestionResponse])
async def analyze_wf(workflow_id: str, req: OptimizationAnalysisRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    wf = await get_workflow(db, workflow_id)
    if not wf or wf.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Workflow not found")
    suggestions = await analyze_workflow(db, workflow_id, req.run_id)
    return [OptimizationSuggestionResponse.model_validate(s) for s in suggestions]


@router.get("/workflows/{workflow_id}/suggestions", response_model=list[OptimizationSuggestionResponse])
async def list_suggestions(workflow_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    wf = await get_workflow(db, workflow_id)
    if not wf or wf.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Workflow not found")
    result = await db.execute(
        select(OptimizationSuggestion)
        .where(OptimizationSuggestion.workflow_id == workflow_id)
        .order_by(OptimizationSuggestion.created_at.desc())
    )
    suggestions = result.scalars().all()
    return [OptimizationSuggestionResponse.model_validate(s) for s in suggestions]


@router.post("/optimizations/apply", response_model=OptimizationSuggestionResponse)
async def apply_opt(req: ApplyOptimizationRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    suggestion = await apply_optimization(db, req.suggestion_id)
    if not suggestion:
        raise HTTPException(status_code=404, detail="Optimization suggestion not found")
    return OptimizationSuggestionResponse.model_validate(suggestion)


@router.get("/analytics/summary")
async def analytics_summary(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    wfs = await get_user_workflows(db, user.id)
    total_runs = 0
    total_executions = 0
    success_count = 0
    total_duration = 0.0
    for wf in wfs:
        runs = await get_workflow_runs(db, wf.id)
        total_runs += len(runs)
        for r in runs:
            total_executions += len(r.task_executions)
            if r.status.value == "completed":
                success_count += 1
            if r.total_duration_ms:
                total_duration += r.total_duration_ms
    return {
        "total_workflows": len(wfs),
        "total_runs": total_runs,
        "total_task_executions": total_executions,
        "successful_runs": success_count,
        "failed_runs": total_runs - success_count,
        "success_rate": (success_count / total_runs * 100) if total_runs else 0,
        "total_duration_hours": total_duration / 3600000 if total_duration else 0,
    }
