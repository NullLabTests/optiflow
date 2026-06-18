from pydantic import BaseModel
from datetime import datetime
from app.models.optimization import SuggestionType, SuggestionStatus


class OptimizationSuggestionResponse(BaseModel):
    id: str
    workflow_id: str
    source_run_id: str | None = None
    suggestion_type: SuggestionType
    title: str
    description: str | None = None
    target_task_id: str | None = None
    estimated_improvement_pct: float | None = None
    status: SuggestionStatus
    proposed_changes: dict
    applied: bool
    applied_at: datetime | None = None
    result_after_apply: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class OptimizationAnalysisRequest(BaseModel):
    workflow_id: str
    run_id: str | None = None


class ApplyOptimizationRequest(BaseModel):
    suggestion_id: str
