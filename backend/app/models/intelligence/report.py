import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Text, DateTime, ForeignKey, Index, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.enums import ReportStatus

if TYPE_CHECKING:
    from app.models.analysis.analysis_run import AnalysisRun


class Report(Base):
    __tablename__ = "reports"
    __table_args__ = (
        Index("idx_reports_run_id", "analysis_run_id"),
        Index("idx_reports_status", "status"),
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
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    report_type: Mapped[str] = mapped_column(
        String(100),
        default="EXECUTIVE_INTELLIGENCE_DOSSIER",
        nullable=False,
    )
    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus, name="report_status", schema="intelligence"),
        nullable=False,
        default=ReportStatus.PENDING,
    )
    executive_summary: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    file_path: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True,
        comment="Local filesystem or artifact path to compiled PDF dossier",
    )
    methodology_version: Mapped[str] = mapped_column(
        String(50),
        default="1.0.0",
        nullable=False,
    )
    generated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    analysis_run: Mapped["AnalysisRun"] = relationship("AnalysisRun", back_populates="reports")

    def __repr__(self) -> str:
        return f"<Report(id={self.id}, title='{self.title}', status='{self.status}')>"
