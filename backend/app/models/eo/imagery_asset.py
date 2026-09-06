import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from sqlalchemy import String, Float, BigInteger, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.eo.imagery_scene import ImageryScene


class ImageryAsset(Base):
    __tablename__ = "imagery_assets"
    __table_args__ = (
        Index("idx_assets_scene_id", "imagery_scene_id"),
        Index("idx_assets_key", "asset_key"),
        {"schema": "eo"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    imagery_scene_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("eo.imagery_scenes.id", ondelete="CASCADE"),
        nullable=False,
    )
    asset_key: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Asset identifier within scene e.g. B02, B03, B04, B08, VV, VH, visual",
    )
    href: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
        comment="Direct asset URI (HTTP/S3/GCS or local COG storage)",
    )
    media_type: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="e.g. image/tiff; application=geotiff; profile=cloud-optimized",
    )
    roles: Mapped[Optional[List[str]]] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
        comment="STAC asset roles e.g. ['data', 'reflectance'], ['overview'], ['metadata']",
    )
    title: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    band_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        comment="Spectral/radar metadata e.g. center_wavelength, fwhm, polarization",
    )
    gsd: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Ground sample distance / spatial resolution in meters",
    )
    nodata: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    file_size: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
        comment="Byte size of the asset if known",
    )
    checksum: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
        comment="SHA-256 or MD5 checksum if provided by source",
    )
    is_cloud_optimized: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="True if asset supports HTTP range requests / COG windowing",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    scene: Mapped["ImageryScene"] = relationship("ImageryScene", back_populates="assets")

    def __repr__(self) -> str:
        return f"<ImageryAsset(id={self.id}, key='{self.asset_key}', scene_id={self.imagery_scene_id})>"
