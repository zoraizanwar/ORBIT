import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Float, DateTime, ForeignKey, Index, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.enums import EpistemicLevel

if TYPE_CHECKING:
    from app.models.analysis.analysis_run import AnalysisRun


class Measurement(Base):
    __tablename__ = "measurements"
    __table_args__ = (
        Index("idx_measurements_run_id", "analysis_run_id"),
        Index("idx_measurements_type", "measurement_type"),
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
    measurement_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="e.g. mean_ndvi, mean_ndwi, affected_area_km2, vegetation_loss_ha, built_up_km2, road_length_km",
    )
    # Authoritative numerical value (read-only for downstream AI synthesizers)
    value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    unit: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="km2, ha, percent, index_delta, meters",
    )
    uncertainty: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Physical plus/minus error bound (+/- delta)",
    )
    epistemic_level: Mapped[EpistemicLevel] = mapped_column(
        Enum(EpistemicLevel, name="epistemic_level", schema="intelligence"),
        nullable=False,
        default=EpistemicLevel.CALCULATED,
    )
    methodology: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Deterministic PostGIS ST_Area(geom::geography), band math equation, etc.",
    )
    source: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Sensor telemetry ID or algorithm reference",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    analysis_run: Mapped["AnalysisRun"] = relationship("AnalysisRun", back_populates="measurements")

    def __repr__(self) -> str:
        return f"<Measurement(id={self.id}, type='{self.measurement_type}', value={self.value} {self.unit})>"
