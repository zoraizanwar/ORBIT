import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Float, DateTime, ForeignKey, Index, CheckConstraint, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry
from app.db.base import Base
from app.models.enums import EvidenceStrength

if TYPE_CHECKING:
    from app.models.analysis.analysis_run import AnalysisRun


class DetectedChange(Base):
    __tablename__ = "detected_changes"
    __table_args__ = (
        Index("idx_changes_geometry", "geometry", postgresql_using="gist"),
        Index("idx_changes_run_id", "analysis_run_id"),
        Index("idx_changes_type", "change_type"),
        CheckConstraint(
            "confidence >= 0.0 AND confidence <= 1.0",
            name="check_change_confidence_range",
        ),
        CheckConstraint(
            "after_date >= before_date",
            name="check_change_dates_logical",
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
    change_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="e.g. VEGETATION_LOSS, VEGETATION_GAIN, URBAN_EXPANSION, WATER_RECESSION, WATER_INUNDATION, ROAD_CONSTRUCTION",
    )
    # Canonical SRID 4326 MultiPolygon geometry representation
    geometry: Mapped[Geometry] = mapped_column(
        Geometry(geometry_type="MULTIPOLYGON", srid=4326, spatial_index=False),
        nullable=False,
    )
    # Authoritative geodesic affected surface area in square kilometers
    affected_area: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Calculated surface area in km2 via PostGIS ST_Area(geom::geography)",
    )
    percentage_change: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Relative magnitude of transition (%)",
    )
    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0,
        comment="Statistical classification confidence score (0.0 - 1.0)",
    )
    evidence_strength: Mapped[EvidenceStrength] = mapped_column(
        Enum(EvidenceStrength, name="evidence_strength", schema="intelligence"),
        nullable=False,
        default=EvidenceStrength.STRONG,
        comment="First-class data/sensor/lineage pedigree rating (STRONG, MODERATE, LIMITED, INSUFFICIENT)",
    )
    detection_method: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="e.g. Tier_2_Adaptive_Otsu_dNDVI, Tier_2_CCDC_Break, Tier_3_UNet_Semantic",
    )
    before_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    after_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    analysis_run: Mapped["AnalysisRun"] = relationship("AnalysisRun", back_populates="detected_changes")

    def __repr__(self) -> str:
        return f"<DetectedChange(id={self.id}, type='{self.change_type}', area_km2={self.affected_area:.2f})>"
