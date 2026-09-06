import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey, Index, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.enums import EvidenceStrength, EpistemicLevel

if TYPE_CHECKING:
    from app.models.analysis.analysis_run import AnalysisRun
    from app.models.intelligence.intelligence_event import IntelligenceEvent
    from app.models.intelligence.evidence_relationship import EvidenceRelationship


class EvidenceRecord(Base):
    __tablename__ = "evidence_records"
    __table_args__ = (
        Index("idx_evidence_run_id", "analysis_run_id"),
        Index("idx_evidence_intel_event_id", "intelligence_event_id"),
        Index("idx_evidence_source_id", "source_id"),
        Index("idx_evidence_checksum", "input_checksum"),
        {"schema": "intelligence"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    analysis_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("analysis.runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    intelligence_event_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("intelligence.intelligence_events.id", ondelete="SET NULL"),
        nullable=True,
    )
    source_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="SATELLITE_TELEMETRY, ROAD_VECTOR_REGISTRY, STATISTICAL_MODEL, GEODESIC_CALCULATION, DETECTED_CHANGE",
    )
    source_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="e.g. S2A_MSIL2A_20240720..., OSM_Way_1289412, chg-uuid",
    )
    claim_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="e.g. DEFORESTATION_SURGE_AREA, WATER_SURFACE_CONTRACTION, ROAD_CLEARING_LENGTH, SPECTRAL_INDEX_SHIFT",
    )
    claim_reference: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Target metric name or polygon reference",
    )
    input_checksum: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="Cryptographic SHA-256 hash of raw input telemetry/vector asset",
    )
    processing_version: Mapped[str] = mapped_column(
        String(50),
        default="ORBIT-Engine-v1.0.0",
        nullable=False,
    )
    algorithm: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="e.g. PostGIS_ST_Area_Spheroid, Adaptive_Otsu_dNDVI, CCDC_Harmonic",
    )
    parameters: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )
    evidence_strength: Mapped[EvidenceStrength] = mapped_column(
        Enum(EvidenceStrength, name="evidence_strength", schema="intelligence"),
        nullable=False,
        default=EvidenceStrength.STRONG,
    )
    epistemic_level: Mapped[EpistemicLevel] = mapped_column(
        Enum(EpistemicLevel, name="epistemic_level", schema="intelligence"),
        nullable=False,
        default=EpistemicLevel.CALCULATED,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    analysis_run: Mapped["AnalysisRun"] = relationship("AnalysisRun", back_populates="evidence_records")
    intelligence_event: Mapped[Optional["IntelligenceEvent"]] = relationship(
        "IntelligenceEvent",
        back_populates="evidence_records",
    )
    outgoing_relationships: Mapped[List["EvidenceRelationship"]] = relationship(
        "EvidenceRelationship",
        back_populates="source_evidence",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<EvidenceRecord(id={self.id}, claim='{self.claim_type}', source='{self.source_id}')>"

