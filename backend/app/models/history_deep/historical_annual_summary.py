import uuid
from datetime import datetime, timezone
from typing import Dict, Any, TYPE_CHECKING
from sqlalchemy import Integer, DateTime, ForeignKey, Index, UniqueConstraint, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.enums import SupportClassification

if TYPE_CHECKING:
    from app.models.workspace.area_of_interest import AreaOfInterest


class HistoricalAnnualSummary(Base):
    __tablename__ = "historical_annual_summaries"
    __table_args__ = (
        UniqueConstraint("area_of_interest_id", "year", name="uq_aoi_historical_year"),
        Index("idx_historical_aoi_year", "area_of_interest_id", "year"),
        Index("idx_historical_support", "support_classification"),
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
    year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Calendar year (e.g. 1972 - 2026)",
    )
    support_classification: Mapped[SupportClassification] = mapped_column(
        Enum(SupportClassification, name="support_classification", schema="history_deep"),
        nullable=False,
        default=SupportClassification.STRONGLY_SUPPORTED,
        comment="STRONGLY_SUPPORTED, PARTIALLY_SUPPORTED, ESTIMATED, UNAVAILABLE",
    )
    summary_data: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment="Aggregated metrics: mean_ndvi, mean_ndwi, built_up_km2, vegetation_km2, water_km2, new_roads_km",
    )
    data_sources: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment="List of satellite scenes, telemetry providers, and sensor IDs utilized",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    area_of_interest: Mapped["AreaOfInterest"] = relationship("AreaOfInterest", back_populates="historical_annual_summaries")

    def __repr__(self) -> str:
        return f"<HistoricalAnnualSummary(aoi={self.area_of_interest_id}, year={self.year}, support='{self.support_classification}')>"
