from datetime import datetime, timezone
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Text, Boolean, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.enums import SensingModality

if TYPE_CHECKING:
    from app.models.eo.imagery_scene import ImageryScene


class DatasetRegistry(Base):
    __tablename__ = "dataset_registry"
    __table_args__ = {"schema": "eo"}

    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        comment="Canonical dataset ID: e.g. copernicus-s2-l2a, copernicus-s1-grd, usgs-landsat-c2l2",
    )
    provider: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="e.g. European Space Agency, USGS, OpenStreetMap Foundation",
    )
    dataset_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    dataset_version: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    modality: Mapped[SensingModality] = mapped_column(
        Enum(SensingModality, name="sensing_modality", schema="eo"),
        nullable=False,
        default=SensingModality.OPTICAL,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    license: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="e.g. EU Copernicus Open Data Policy, Public Domain, ODbL 1.0",
    )
    attribution: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Mandatory legal attribution text to include in reports & UI",
    )
    terms_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    redistribution_allowed: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    commercial_use_allowed: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    api_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    documentation_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    active: Mapped[bool] = mapped_column(
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

    # Relationships
    scenes: Mapped[List["ImageryScene"]] = relationship(
        "ImageryScene",
        back_populates="dataset",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<DatasetRegistry(id='{self.id}', provider='{self.provider}', modality='{self.modality}')>"
