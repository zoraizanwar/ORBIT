import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Integer, Float, Boolean, BigInteger, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from geoalchemy2 import Geometry
from app.db.base import Base


class RoadFeature(Base):
    __tablename__ = "road_features"
    __table_args__ = (
        Index("idx_roads_geometry", "geometry", postgresql_using="gist"),
        Index("idx_roads_osm_id", "osm_id"),
        Index("idx_roads_highway_class", "highway_class"),
        {"schema": "geo"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    osm_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        nullable=False,
    )
    # Canonical SRID 4326 LineString geometry representation
    geometry: Mapped[Geometry] = mapped_column(
        Geometry(geometry_type="LINESTRING", srid=4326, spatial_index=False),
        nullable=False,
    )
    highway_class: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="OSM classification: motorway, trunk, primary, secondary, tertiary, residential, service, track, path",
    )
    name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    ref: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Route reference (e.g. M1, I-95, Route 66)",
    )
    surface: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="paved, unpaved, asphalt, gravel, concrete",
    )
    lanes: Mapped[Optional[int]] = mapped_column(
        Integer,
        default=1,
        nullable=True,
    )
    maxspeed: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Speed limit in km/h",
    )
    oneway: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    access: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="yes, private, permissive, destination, no",
    )
    bridge: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    tunnel: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    source: Mapped[str] = mapped_column(
        String(50),
        default="OpenStreetMap",
        nullable=False,
    )
    source_version: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    # Authoritative geodesic length in meters calculated on spheroid
    length_m: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
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

    def __repr__(self) -> str:
        return f"<RoadFeature(id={self.id}, osm_id={self.osm_id}, class='{self.highway_class}', name='{self.name}')>"
