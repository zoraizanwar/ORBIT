import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, TYPE_CHECKING
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Index, CheckConstraint, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.enums import FuturePredictionType, EvidenceStrength

if TYPE_CHECKING:
    from app.models.workspace.area_of_interest import AreaOfInterest


class FuturePrediction(Base):
    __tablename__ = "future_predictions"
    __table_args__ = (
        Index("idx_predictions_aoi_target", "area_of_interest_id", "target_year"),
        Index("idx_predictions_type", "prediction_type"),
        CheckConstraint(
            "target_year > training_end_year",
            name="check_prediction_target_after_training",
        ),
        CheckConstraint(
            "training_end_year >= training_start_year",
            name="check_prediction_training_years",
        ),
        CheckConstraint(
            "confidence >= 0.0 AND confidence <= 1.0",
            name="check_prediction_confidence_range",
        ),
        CheckConstraint(
            "upper_bound IS NULL OR lower_bound IS NULL OR upper_bound >= lower_bound",
            name="check_prediction_bounds_logical",
        ),
        {"schema": "history_deep"},
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
    prediction_type: Mapped[FuturePredictionType] = mapped_column(
        Enum(FuturePredictionType, name="future_prediction_type", schema="history_deep"),
        nullable=False,
        comment="URBAN_EXPANSION, VEGETATION_TREND, WATER_COVERAGE, ROAD_DEVELOPMENT, LAND_USE_CHANGE",
    )
    target_year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Future projection year (e.g. 2030, 2035, 2050)",
    )
    prediction_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Model point forecast value",
    )
    lower_bound: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Lower confidence interval boundary (e.g. 95% CI)",
    )
    upper_bound: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Upper confidence interval boundary (e.g. 95% CI)",
    )
    unit: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="km2, ha, index_value, percent",
    )
    model_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="e.g. Prophet_Trend, ARIMA_Seasonal, Cellular_Automata_Urban, LandChangeModeler",
    )
    model_version: Mapped[str] = mapped_column(
        String(50),
        default="1.0.0",
        nullable=False,
    )
    training_start_year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Start of calibration baseline (e.g. 2000)",
    )
    training_end_year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="End of calibration baseline (e.g. 2024)",
    )
    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.8,
        comment="Model statistical confidence score (0.0 - 1.0)",
    )
    evidence_strength: Mapped[EvidenceStrength] = mapped_column(
        Enum(EvidenceStrength, name="evidence_strength", schema="intelligence"),
        nullable=False,
        default=EvidenceStrength.MODERATE,
    )
    scenario: Mapped[str] = mapped_column(
        String(100),
        default="BUSINESS_AS_USUAL",
        nullable=False,
        comment="e.g. BUSINESS_AS_USUAL, HIGH_GROWTH, CONSERVATION_STRICT",
    )
    metric: Mapped[str] = mapped_column(
        String(100),
        default="NDVI",
        nullable=False,
        comment="e.g. NDVI, NDWI, NDBI, SAVI, BUILT_UP_AREA",
    )
    analysis_run_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("analysis.runs.id", ondelete="SET NULL"),
        nullable=True,
    )
    assumptions: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )
    limitations: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
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
    area_of_interest: Mapped["AreaOfInterest"] = relationship("AreaOfInterest", back_populates="future_predictions")

    def __repr__(self) -> str:
        return f"<FuturePrediction(aoi={self.area_of_interest_id}, metric='{self.metric}', target={self.target_year})>"
