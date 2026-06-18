import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, ForeignKey, JSON, Boolean, Float, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import enum


class SuggestionType(str, enum.Enum):
    PARALLELIZE = "parallelize"
    CACHE = "cache"
    ALGORITHM_SWAP = "algorithm_swap"
    RESOURCE_ALLOCATION = "resource_allocation"
    CODE_IMPROVEMENT = "code_improvement"
    RESTRUCTURE = "restructure"
    REMOVE_REDUNDANCY = "remove_redundancy"


class SuggestionStatus(str, enum.Enum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    APPLIED = "applied"
    REJECTED = "rejected"
    FAILED = "failed"


class OptimizationSuggestion(Base):
    __tablename__ = "optimization_suggestions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id: Mapped[str] = mapped_column(String, ForeignKey("workflows.id"), nullable=False)
    source_run_id: Mapped[str] = mapped_column(String, ForeignKey("workflow_runs.id"), nullable=True)
    suggestion_type: Mapped[SuggestionType] = mapped_column(SAEnum(SuggestionType), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    target_task_id: Mapped[str] = mapped_column(String, nullable=True)
    estimated_improvement_pct: Mapped[float] = mapped_column(Float, nullable=True)
    status: Mapped[SuggestionStatus] = mapped_column(SAEnum(SuggestionStatus), default=SuggestionStatus.PROPOSED)
    proposed_changes: Mapped[dict] = mapped_column(JSON, default=dict)
    applied: Mapped[bool] = mapped_column(Boolean, default=False)
    applied_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    result_after_apply: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    workflow = relationship("Workflow")
