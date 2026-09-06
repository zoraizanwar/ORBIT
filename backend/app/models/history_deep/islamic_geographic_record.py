import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Text, Float, DateTime, Index, CheckConstraint, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from geoalchemy2 import Geometry
from app.db.base import Base
from app.models.enums import IslamicSourceGrade


class IslamicGeographicRecord(Base):
    __tablename__ = "islamic_geographic_records"
    __table_args__ = (
        Index("idx_islamic_geo_geometry", "geometry", postgresql_using="gist"),
        Index("idx_islamic_classification", "classification"),
        CheckConstraint(
            "confidence >= 0.0 AND confidence <= 1.0",
            name="check_islamic_record_confidence_range",
        ),
        {"schema": "history_deep"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    source_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="QURANIC_AYAH, HADITH_NARRATION, SCHOLARLY_GEOGRAPHY, HISTORICAL_CHRONICLE",
    )
    classification: Mapped[IslamicSourceGrade] = mapped_column(
        Enum(IslamicSourceGrade, name="islamic_source_grade", schema="history_deep"),
        nullable=False,
        comment="QURAN, MUTAWATIR_HADITH, AHAD_SAHIH, SCHOLARLY_IJMA, HISTORICAL_TARIKH, UNVERIFIED_ISRAILIYYAT",
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="English translation and textual geographic narrative",
    )
    date_reference: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Historical era e.g. Prophetic Era (610-632 CE), Classical Abbasid (8th-10th c. CE)",
    )
    geographic_reference: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Historical toponym (e.g. Adna al-Ard / Dead Sea Depression, Hijaz Highlands, Yathrib Oasis)",
    )
    # PostGIS geometry for spatial representation where geographical coordinates are historically established
    geometry: Mapped[Optional[Geometry]] = mapped_column(
        Geometry(geometry_type="GEOMETRY", srid=4326, spatial_index=False),
        nullable=True,
    )
    source: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Primary textual citation: Surah Al-Rum (30:2-4), Sahih Muslim 157, Mu'jam al-Buldan",
    )
    source_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    scholarly_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Commentaries from Ibn Kathir, Al-Qurtubi, Yaqut al-Hamawi, Al-Tabari",
    )
    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<IslamicGeographicRecord(title='{self.title}', grade='{self.classification}')>"
