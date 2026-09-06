import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, TYPE_CHECKING
from sqlalchemy import String, Float, DateTime, ForeignKey, Index, CheckConstraint, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry
from app.db.base import Base
from app.models.enums import SensingModality

if TYPE_CHECKING:
    from app.models.eo.dataset_registry import DatasetRegistry
    from app.models.eo.imagery_asset import ImageryAsset


class ImageryScene(Base):
    __tablename__ = "imagery_scenes"
    __table_args__ = (
        Index("idx_scenes_geometry", "geometry", postgresql_using="gist"),
        Index("idx_scenes_acquisition_datetime", "acquisition_datetime"),
        Index("idx_scenes_dataset_id", "dataset_id"),
        CheckConstraint(
            "cloud_cover IS NULL OR (cloud_cover >= 0.0 AND cloud_cover <= 100.0)",
            name="check_scene_cloud_cover_range",
        ),
        {"schema": "eo"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    dataset_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("eo.dataset_registry.id", ondelete="CASCADE"),
        nullable=False,
    )
    provider_scene_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        comment="Provider scene identifier e.g. S2A_MSIL2A_20240720T...",
    )
    acquisition_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    platform: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="e.g. Sentinel-2A, Sentinel-1B, Landsat-9",
    )
    sensor: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="e.g. MSI, C-SAR, OLI-2",
    )
    modality: Mapped[SensingModality] = mapped_column(
        Enum(SensingModality, name="sensing_modality", schema="eo"),
        nullable=False,
        default=SensingModality.OPTICAL,
    )
    cloud_cover: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Cloud cover percentage (0.0 - 100.0)",
    )
    processing_level: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="e.g. Level-2A (Surface Reflectance), Level-1C (TOA), GRD",
    )
    spatial_resolution: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Ground Sample Distance in meters (e.g. 10.0, 30.0)",
    )
    # Canonical footprint polygon in SRID 4326
    geometry: Mapped[Geometry] = mapped_column(
        Geometry(geometry_type="POLYGON", srid=4326, spatial_index=False),
        nullable=False,
    )
    asset_url: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True,
        comment="Direct STAC asset URI or local COG storage path",
    )
    thumbnail_url: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True,
    )
    metadata_payload: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment="Raw STAC properties, sun azimuth/elevation, incidence angles",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    dataset: Mapped["DatasetRegistry"] = relationship("DatasetRegistry", back_populates="scenes")
    assets: Mapped[List["ImageryAsset"]] = relationship(
        "ImageryAsset",
        back_populates="scene",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<ImageryScene(id={self.id}, scene_id='{self.provider_scene_id}', platform='{self.platform}')>"
