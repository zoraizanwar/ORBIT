import uuid
from datetime import datetime, timezone
from typing import Dict, Any, TYPE_CHECKING
from sqlalchemy import String, Float, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.intelligence.evidence_record import EvidenceRecord


class EvidenceRelationship(Base):
    __tablename__ = "evidence_relationships"
    __table_args__ = (
        Index("idx_rel_source_id", "source_evidence_id"),
        Index("idx_rel_target_type", "target_entity_type"),
        Index("idx_rel_type", "relationship_type"),
        {"schema": "intelligence"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    source_evidence_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("intelligence.evidence_records.id", ondelete="CASCADE"),
        nullable=False,
    )
    target_entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="INTELLIGENCE_EVENT, DETECTED_CHANGE, MEASUREMENT, EVIDENCE_RECORD, ROAD_FEATURE, SCENE",
    )
    target_entity_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Target primary key string or UUID representation",
    )
    relationship_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="DERIVED_FROM, SUPPORTS, CORROBORATES, CONTRADICTS, LOCATED_IN, TEMPORALLY_ALIGNS, SPATIALLY_OVERLAPS, SOURCE_OF",
    )
    weight: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        nullable=False,
        comment="Confidence / strength weight for graph traversal",
    )
    metadata_payload: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment="Spatial overlap pct, distance, delta difference, algorithm version",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    source_evidence: Mapped["EvidenceRecord"] = relationship(
        "EvidenceRecord",
        back_populates="outgoing_relationships",
    )

    def __repr__(self) -> str:
        return f"<EvidenceRelationship({self.source_evidence_id} --[{self.relationship_type}]--> {self.target_entity_type}:{self.target_entity_id})>"
