from pydantic import BaseModel
from datetime import datetime
from typing import Any


class WorkflowTaskCreate(BaseModel):
    id: str | None = None
    name: str
    task_type: str = "python"
    config: dict = {}
    position_x: float = 0
    position_y: float = 0


class WorkflowEdgeCreate(BaseModel):
    source_task_id: str
    target_task_id: str


class WorkflowCreate(BaseModel):
    name: str
    description: str | None = None
    tasks: list[WorkflowTaskCreate] = []
    edges: list[WorkflowEdgeCreate] = []
    dag_json: str | None = None


class WorkflowUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    tasks: list[WorkflowTaskCreate] | None = None
    edges: list[WorkflowEdgeCreate] | None = None
    dag_json: str | None = None


class WorkflowTaskResponse(BaseModel):
    id: str
    name: str
    task_type: str
    config: dict
    position_x: float
    position_y: float

    model_config = {"from_attributes": True}


class WorkflowEdgeResponse(BaseModel):
    id: str
    source_task_id: str
    target_task_id: str

    model_config = {"from_attributes": True}


class WorkflowResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    owner_id: str
    version: int
    tasks: list[WorkflowTaskResponse] = []
    edges: list[WorkflowEdgeResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WorkflowListResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    version: int
    task_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NLWorkflowRequest(BaseModel):
    prompt: str
