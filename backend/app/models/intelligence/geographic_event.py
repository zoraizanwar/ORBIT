import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Text, Float, DateTime, ForeignKey, Index, CheckConstraint, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry
from app.db.base import Base
from app.models.enums import EvidenceStrength

if TYPE_CHECKING:
    from app.models.analysis.analysis_run import AnalysisRun


class GeographicEvent(Base):
    __tablename__ = "geographic_events"
    __table_args__ = (
        Index("idx_events_geometry", "geometry", postgresql_using="gist"),
        Index("idx_events_run_id", "analysis_run_id"),
        Index("idx_events_type", "event_type"),
        CheckConstraint(
            "confidence >= 0.0 AND confidence <= 1.0",
            name="check_event_confidence_range",
        ),
        CheckConstraint(
            "end_date >= start_date",
            name="check_event_dates_logical",
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
    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="e.g. URBAN_SPRAWL_EXPANSION, CANOPY_DEFORESTATION_SURGE, RESERVOIR_DESICCATION, ROAD_CORRIDOR_CLEARING, WILDFIRE_BURN_SCAR",
    )
    # Canonical SRID 4326 MultiPolygon geometry representation
    geometry: Mapped[Geometry] = mapped_column(
        Geometry(geometry_type="MULTIPOLYGON", srid=4326, spatial_index=False),
        nullable=False,
    )
    severity: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="CRITICAL, HIGH, MODERATE, LOW, INFORMATIONAL",
    )
    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0,
    )
    evidence_strength: Mapped[EvidenceStrength] = mapped_column(
        Enum(EvidenceStrength, name="evidence_strength", schema="intelligence"),
        nullable=False,
        default=EvidenceStrength.STRONG,
    )
    start_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    end_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    analysis_run: Mapped["AnalysisRun"] = relationship("AnalysisRun", back_populates="geographic_events")

    def __repr__(self) -> str:
        return f"<GeographicEvent(id={self.id}, type='{self.event_type}', severity='{self.severity}')>"
