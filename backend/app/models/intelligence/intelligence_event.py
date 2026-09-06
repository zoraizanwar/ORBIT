import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from sqlalchemy import String, Float, DateTime, ForeignKey, Index, CheckConstraint, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry
from app.db.base import Base
from app.models.enums import EpistemicLevel, EvidenceStrength

if TYPE_CHECKING:
    from app.models.analysis.analysis_run import AnalysisRun
    from app.models.workspace.area_of_interest import AreaOfInterest
    from app.models.intelligence.evidence_record import EvidenceRecord
    from app.models.intelligence.evidence_relationship import EvidenceRelationship


class IntelligenceEvent(Base):
    __tablename__ = "intelligence_events"
    __table_args__ = (
        Index("idx_intel_events_geometry", "geometry", postgresql_using="gist"),
        Index("idx_intel_events_run_id", "analysis_run_id"),
        Index("idx_intel_events_type", "intelligence_type"),
        Index("idx_intel_events_strength", "evidence_strength"),
        CheckConstraint(
            "confidence >= 0.0 AND confidence <= 1.0",
            name="check_intel_event_confidence_range",
        ),
        CheckConstraint(
            "end_date >= start_date",
            name="check_intel_event_dates_logical",
        ),
        {"schema": "intelligence"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    analysis_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("analysis.runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    area_of_interest_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspace.areas_of_interest.id", ondelete="SET NULL"),
        nullable=True,
    )
    intelligence_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="VEGETATION_CHANGE, WATER_CHANGE, URBAN_EXPANSION, URBAN_REDUCTION, INFRASTRUCTURE_CHANGE, ROAD_CHANGE, LAND_USE_CHANGE, ENVIRONMENTAL_CHANGE, SPATIAL_ANOMALY, MULTI_INDICATOR_EVENT",
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    # Canonical SRID 4326 MultiPolygon geometry representation
    geometry: Mapped[Geometry] = mapped_column(
        Geometry(geometry_type="MULTIPOLYGON", srid=4326, spatial_index=False),
        nullable=False,
    )
    # Geodesic affected surface area in square kilometers
    affected_area: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Calculated surface area in km2",
    )
    start_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    end_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    evidence_strength: Mapped[EvidenceStrength] = mapped_column(
        Enum(EvidenceStrength, name="evidence_strength", schema="intelligence"),
        nullable=False,
        default=EvidenceStrength.STRONG,
    )
    epistemic_level: Mapped[EpistemicLevel] = mapped_column(
        Enum(EpistemicLevel, name="epistemic_level", schema="intelligence"),
        nullable=False,
        default=EpistemicLevel.CALCULATED,
    )
    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0,
    )
    rule_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Deterministic rule identifier (e.g. RULE_MULTI_URBAN_EXPANSION_v1)",
    )
    rule_version: Mapped[str] = mapped_column(
        String(50),
        default="1.0.0",
        nullable=False,
    )
    algorithm_version: Mapped[str] = mapped_column(
        String(50),
        default="ORBIT-Intelligence-v1.0",
        nullable=False,
    )
    quality_metadata: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment="Completeness, supporting count, conflicting count",
    )
    provenance: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment="Full calculation methodology and source traces",
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="ACTIVE",
        nullable=False,
        comment="ACTIVE, ARCHIVED, VERIFIED, CONTRADICTED",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    analysis_run: Mapped["AnalysisRun"] = relationship("AnalysisRun")
    area_of_interest: Mapped[Optional["AreaOfInterest"]] = relationship("AreaOfInterest")
    evidence_records: Mapped[List["EvidenceRecord"]] = relationship(
        "EvidenceRecord",
        back_populates="intelligence_event",
    )

    def __repr__(self) -> str:
        return f"<IntelligenceEvent(id={self.id}, type='{self.intelligence_type}', area={self.affected_area:.2f}km2)>"
