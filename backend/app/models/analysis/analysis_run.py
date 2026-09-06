import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from sqlalchemy import String, Text, DateTime, ForeignKey, Index, CheckConstraint, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.enums import AnalysisStatus

if TYPE_CHECKING:
    from app.models.workspace.project import Project
    from app.models.workspace.area_of_interest import AreaOfInterest
    from app.models.intelligence.measurement import Measurement
    from app.models.intelligence.detected_change import DetectedChange
    from app.models.intelligence.geographic_event import GeographicEvent
    from app.models.intelligence.evidence_record import EvidenceRecord
    from app.models.intelligence.report import Report


class AnalysisRun(Base):
    __tablename__ = "runs"
    __table_args__ = (
        Index("idx_runs_status", "status"),
        Index("idx_runs_project_id", "project_id"),
        Index("idx_runs_aoi_id", "area_of_interest_id"),
        CheckConstraint(
            "end_date >= start_date",
            name="check_analysis_run_dates",
        ),
        {"schema": "analysis"},
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
    )
    area_of_interest_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspace.areas_of_interest.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[AnalysisStatus] = mapped_column(
        Enum(AnalysisStatus, name="analysis_status", schema="analysis"),
        nullable=False,
        default=AnalysisStatus.QUEUED,
    )
    analysis_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="e.g. BI_TEMPORAL_CHANGE, MULTI_YEAR_TIMELINE, URBAN_EXPANSION, FLOOD_INUNDATION",
    )
    start_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Baseline temporal boundary",
    )
    end_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Target temporal boundary",
    )
    parameters: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment="Algorithm thresholds, indices requested, sensor modality filters",
    )
    pipeline_version: Mapped[str] = mapped_column(
        String(50),
        default="1.0.0",
        nullable=False,
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
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
    project: Mapped["Project"] = relationship("Project", back_populates="analysis_runs")
    area_of_interest: Mapped["AreaOfInterest"] = relationship("AreaOfInterest", back_populates="analysis_runs")
    measurements: Mapped[List["Measurement"]] = relationship(
        "Measurement",
        back_populates="analysis_run",
        cascade="all, delete-orphan",
    )
    detected_changes: Mapped[List["DetectedChange"]] = relationship(
        "DetectedChange",
        back_populates="analysis_run",
        cascade="all, delete-orphan",
    )
    geographic_events: Mapped[List["GeographicEvent"]] = relationship(
        "GeographicEvent",
        back_populates="analysis_run",
        cascade="all, delete-orphan",
    )
    evidence_records: Mapped[List["EvidenceRecord"]] = relationship(
        "EvidenceRecord",
        back_populates="analysis_run",
        cascade="all, delete-orphan",
    )
    reports: Mapped[List["Report"]] = relationship(
        "Report",
        back_populates="analysis_run",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<AnalysisRun(id={self.id}, type='{self.analysis_type}', status='{self.status}')>"
