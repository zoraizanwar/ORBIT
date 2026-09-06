import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, TYPE_CHECKING
from sqlalchemy import String, Float, DateTime, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.workspace.area_of_interest import AreaOfInterest
    from app.models.analysis.analysis_run import AnalysisRun
    from app.models.intelligence.intelligence_event import IntelligenceEvent


class AIInterpretation(Base):
    __tablename__ = "ai_interpretations"
    __table_args__ = (
        Index("idx_ai_interp_aoi", "area_of_interest_id"),
        Index("idx_ai_interp_type", "interpretation_type"),
        Index("idx_ai_interp_created", "created_at"),
        {"schema": "intelligence"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    area_of_interest_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspace.areas_of_interest.id", ondelete="CASCADE"),
        nullable=False,
    )
    analysis_run_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("analysis.runs.id", ondelete="SET NULL"),
        nullable=True,
    )
    intelligence_event_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("intelligence.intelligence_events.id", ondelete="SET NULL"),
        nullable=True,
    )
    interpretation_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="GENERAL_EVALUATION",
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    executive_summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    epistemic_level: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="AI_INTERPRETED",
    )
    evidence_package_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    provider_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="ORBIT-LocalReasoner",
    )
    model_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="DeterministicGroundedSynthesizer",
    )
    model_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="1.0.0",
    )
    prompt_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="ORBIT-AI-Prompt-v1",
    )
    uncertainty_statement: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    contradiction_statement: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    temporal_interpretation: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    spatial_interpretation: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    forecast_interpretation: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    provenance: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    claims: Mapped[List["AIClaim"]] = relationship("AIClaim", back_populates="interpretation", cascade="all, delete-orphan")
    recommendations: Mapped[List["AIRecommendation"]] = relationship("AIRecommendation", back_populates="interpretation", cascade="all, delete-orphan")


class AIClaim(Base):
    __tablename__ = "ai_claims"
    __table_args__ = (
        Index("idx_ai_claims_interp", "ai_interpretation_id"),
        Index("idx_ai_claims_type", "claim_type"),
        {"schema": "intelligence"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    ai_interpretation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("intelligence.ai_interpretations.id", ondelete="CASCADE"),
        nullable=False,
    )
    claim_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    claim_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="INTERPRETATION",
    )
    epistemic_level: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="AI_INTERPRETED",
    )
    evidence_ids: Mapped[List[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )
    support_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="SUPPORTED",
    )
    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.95,
    )
    validation_details: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    interpretation: Mapped["AIInterpretation"] = relationship("AIInterpretation", back_populates="claims")


class AIRecommendation(Base):
    __tablename__ = "ai_recommendations"
    __table_args__ = (
        Index("idx_ai_rec_interp", "ai_interpretation_id"),
        Index("idx_ai_rec_priority", "priority"),
        {"schema": "intelligence"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    ai_interpretation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("intelligence.ai_interpretations.id", ondelete="CASCADE"),
        nullable=False,
    )
    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="MONITOR",
    )
    recommendation_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="MEDIUM",
    )
    supporting_evidence_ids: Mapped[List[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )
    uncertainty_note: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    interpretation: Mapped["AIInterpretation"] = relationship("AIInterpretation", back_populates="recommendations")


class AIReport(Base):
    __tablename__ = "ai_reports"
    __table_args__ = (
        Index("idx_ai_reports_aoi", "area_of_interest_id"),
        Index("idx_ai_reports_created", "created_at"),
        {"schema": "intelligence"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    area_of_interest_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspace.areas_of_interest.id", ondelete="CASCADE"),
        nullable=False,
    )
    ai_interpretation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("intelligence.ai_interpretations.id", ondelete="SET NULL"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    report_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="EXECUTIVE_BRIEF",
    )
    report_format: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="MARKDOWN",
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    provenance_hash_sha256: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
