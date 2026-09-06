import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import String, Boolean, BigInteger, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from geoalchemy2 import Geometry
from app.db.base import Base


class GazetteerEntity(Base):
    __tablename__ = "gazetteer_entities"
    __table_args__ = (
        Index("idx_gazetteer_centroid", "centroid", postgresql_using="gist"),
        Index("idx_gazetteer_geometry", "geometry", postgresql_using="gist"),
        Index("idx_gazetteer_normalized_name", "normalized_name"),
        Index("idx_gazetteer_country_code", "country_code"),
        Index("idx_gazetteer_entity_type", "entity_type"),
        {"schema": "geo"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="OpenStreetMap",
        comment="Data provider / source (e.g. OpenStreetMap, GeoNames, NaturalEarth)",
    )
    provider_entity_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )
    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Classification from GeographicEntityType enum (e.g. CITY, COUNTRY, MOUNTAIN)",
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    normalized_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Normalized lowercase alphanumeric string for fast matching",
    )
    alternate_names: Mapped[Optional[List[str]]] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
        comment="Array of multilingual aliases, acronyms, or local transliterations",
    )
    country_code: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
        comment="ISO 3166-1 alpha-2 or alpha-3 code (e.g. PK, BR, US)",
    )
    country_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    admin_level_1: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="State / Province / Region (e.g. Punjab, Mato Grosso, California)",
    )
    admin_level_2: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="District / County / Department",
    )
    admin_level_3: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Sub-district / Municipality / Tehsil",
    )
    population: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
        comment="Estimated resident population for prominence weighting",
    )
    geometry: Mapped[Optional[Geometry]] = mapped_column(
        Geometry(geometry_type="GEOMETRY", srid=4326, spatial_index=False),
        nullable=True,
        comment="Full boundary geometry (Polygon, MultiPolygon, LineString, or Point)",
    )
    centroid: Mapped[Geometry] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=False),
        nullable=False,
        comment="Authoritative centroid point (EPSG:4326)",
    )
    bounding_box: Mapped[Optional[Geometry]] = mapped_column(
        Geometry(geometry_type="POLYGON", srid=4326, spatial_index=False),
        nullable=True,
        comment="Bounding envelope polygon (EPSG:4326)",
    )
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
    )
    source_version: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    is_searchable: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
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
        return f"<GazetteerEntity(id={self.id}, name='{self.name}', type='{self.entity_type}', country='{self.country_code}')>"
