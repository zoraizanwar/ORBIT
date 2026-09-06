import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, Float, DateTime, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class GeologicalEpoch(Base):
    __tablename__ = "geological_epochs"
    __table_args__ = (
        CheckConstraint(
            "start_age >= end_age",
            name="check_geological_age_order",
        ),
        {"schema": "history_deep"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        comment="Epoch/Period name (e.g. Holocene, Pleistocene, Pliocene, Miocene, Cretaceous)",
    )
    start_age: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Start age in Millions of Years Ago (Ma)",
    )
    end_age: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="End age in Millions of Years Ago (Ma)",
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Paleoclimatic, tectonic, and paleo-environmental characteristics",
    )
    evidence_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Stratigraphic Core, Marine Isotope Stage (MIS), Radiometric Isotope, Magnetostratigraphy",
    )
    source: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="International Commission on Stratigraphy (ICS)",
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
        return f"<GeologicalEpoch(name='{self.name}', range='{self.start_age}Ma - {self.end_age}Ma')>"
