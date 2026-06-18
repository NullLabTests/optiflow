from pydantic import BaseModel
from datetime import datetime
from app.models.execution import RunStatus, TaskStatus


class TaskExecutionResponse(BaseModel):
    id: str
    run_id: str
    task_id: str
    task_name: str | None = None
    status: TaskStatus
    attempt_number: int
    started_at: datetime | None = None
    finished_at: datetime | None = None
    duration_ms: float | None = None
    cpu_time_ms: float | None = None
    memory_bytes: int | None = None
    input_size_bytes: int | None = None
    output_size_bytes: int | None = None
    error_message: str | None = None
    logs: str | None = None

    model_config = {"from_attributes": True}


class WorkflowRunResponse(BaseModel):
    id: str
    workflow_id: str
    status: RunStatus
    triggered_by: str
    started_at: datetime | None = None
    finished_at: datetime | None = None
    total_duration_ms: float | None = None
    error_message: str | None = None
    task_executions: list[TaskExecutionResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkflowRunListResponse(BaseModel):
    id: str
    workflow_id: str
    status: RunStatus
    triggered_by: str
    started_at: datetime | None = None
    finished_at: datetime | None = None
    total_duration_ms: float | None = None
    task_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}
