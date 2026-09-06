import uuid
from datetime import datetime, timezone
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Text, Float, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.workspace.project import Project
    from app.models.analysis.analysis_run import AnalysisRun
    from app.models.history_deep.historical_annual_summary import HistoricalAnnualSummary
    from app.models.history_deep.future_prediction import FuturePrediction


class AreaOfInterest(Base):
    __tablename__ = "areas_of_interest"
    __table_args__ = (
        Index("idx_aoi_geometry", "geometry", postgresql_using="gist"),
        Index("idx_aoi_centroid", "centroid", postgresql_using="gist"),
        Index("idx_aoi_bounding_box", "bounding_box", postgresql_using="gist"),
        {"schema": "workspace"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspace.projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    # Canonical SRID 4326 MultiPolygon geometry representation
    geometry: Mapped[Geometry] = mapped_column(
        Geometry(geometry_type="MULTIPOLYGON", srid=4326, spatial_index=False),
        nullable=False,
    )
    # Centroid representation for quick focal point queries
    centroid: Mapped[Optional[Geometry]] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=False),
        nullable=True,
    )
    # Bounding envelope geometry
    bounding_box: Mapped[Optional[Geometry]] = mapped_column(
        Geometry(geometry_type="POLYGON", srid=4326, spatial_index=False),
        nullable=True,
    )
    # Authoritative geodesic surface area in square kilometers
    surface_area_km2: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
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
    project: Mapped["Project"] = relationship("Project", back_populates="areas_of_interest")
    analysis_runs: Mapped[List["AnalysisRun"]] = relationship(
        "AnalysisRun",
        back_populates="area_of_interest",
        cascade="all, delete-orphan",
    )
    historical_annual_summaries: Mapped[List["HistoricalAnnualSummary"]] = relationship(
        "HistoricalAnnualSummary",
        back_populates="area_of_interest",
        cascade="all, delete-orphan",
    )
    future_predictions: Mapped[List["FuturePrediction"]] = relationship(
        "FuturePrediction",
        back_populates="area_of_interest",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<AreaOfInterest(id={self.id}, name='{self.name}', area_km2={self.surface_area_km2:.2f})>"
