"""multi-source earth observation fusion and advanced change analysis

Revision ID: 0010_multi_source_fusion
Revises: 0009_operational_workstation
Create Date: 2026-08-27 02:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0010_multi_source_fusion"
down_revision = "0009_operational_workstation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Ensure eo schema exists
    op.execute("CREATE SCHEMA IF NOT EXISTS eo")

    # 1. eo.observation_alignments
    op.create_table(
        "observation_alignments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("analysis_run_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("source_observation_id", sa.String(length=128), nullable=False),
        sa.Column("target_observation_id", sa.String(length=128), nullable=False),
        sa.Column("temporal_offset_days", sa.Float(), nullable=False),
        sa.Column("spatial_overlap_percentage", sa.Float(), nullable=False),
        sa.Column("source_gsd_m", sa.Float(), nullable=False, server_default="10.0"),
        sa.Column("target_gsd_m", sa.Float(), nullable=False, server_default="10.0"),
        sa.Column("resolution_ratio", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("alignment_status", sa.String(length=32), nullable=False),
        sa.Column("reasons", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("resampling_applied", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("resampling_method", sa.String(length=64), nullable=True),
        sa.Column("is_test_fixture", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("provenance", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema="eo",
    )
    op.create_index(
        "ix_eo_observation_alignments_analysis_run_id",
        "observation_alignments",
        ["analysis_run_id"],
        schema="eo",
    )

    # 2. eo.fusion_results
    op.create_table(
        "fusion_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("fusion_id", sa.String(length=64), unique=True, nullable=False),
        sa.Column("analysis_run_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("aoi_id", sa.String(length=128), nullable=False),
        sa.Column("corroboration_state", sa.String(length=32), nullable=False),
        sa.Column("evidence_strength_score", sa.Float(), nullable=False),
        sa.Column("contradiction_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("supporting_observation_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("contradictory_observation_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("provenance_hash_sha256", sa.String(length=64), nullable=False),
        sa.Column("is_test_fixture", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("full_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema="eo",
    )
    op.create_index(
        "ix_eo_fusion_results_fusion_id",
        "fusion_results",
        ["fusion_id"],
        schema="eo",
    )

    # 3. eo.temporal_change_series
    op.create_table(
        "temporal_change_series",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("analysis_run_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("aoi_id", sa.String(length=128), nullable=False),
        sa.Column("metric", sa.String(length=64), nullable=False),
        sa.Column("observation_count", sa.Integer(), nullable=False),
        sa.Column("valid_observation_count", sa.Integer(), nullable=False),
        sa.Column("time_span_days", sa.Float(), nullable=False),
        sa.Column("net_absolute_delta", sa.Float(), nullable=False),
        sa.Column("net_relative_delta_percentage", sa.Float(), nullable=False),
        sa.Column("overall_state", sa.String(length=32), nullable=False),
        sa.Column("persistence_ratio", sa.Float(), nullable=False),
        sa.Column("recovery_detected", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("summary_statistics", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("is_test_fixture", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema="eo",
    )
    op.create_index(
        "ix_eo_temporal_change_series_metric",
        "temporal_change_series",
        ["metric"],
        schema="eo",
    )


def downgrade() -> None:
    op.drop_table("temporal_change_series", schema="eo")
    op.drop_table("fusion_results", schema="eo")
    op.drop_table("observation_alignments", schema="eo")
