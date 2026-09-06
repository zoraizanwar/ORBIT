"""Operational workstation sessions, scene selections, and analysis jobs

Revision ID: 0009_operational_workstation
Revises: 0008_grounded_ai_intelligence
Create Date: 2026-08-27 02:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0009_operational_workstation'
down_revision: Union[str, None] = '0008_grounded_ai_intelligence'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 0. Ensure operational schema exists
    op.execute("CREATE SCHEMA IF NOT EXISTS operational;")

    # 1. operational.aoi_sessions
    op.create_table(
        'aoi_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('geometry', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('bbox', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('area_km2', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        schema='operational'
    )
    op.create_index('idx_operational_aoi_sessions_created', 'aoi_sessions', ['created_at'], schema='operational')

    # 2. operational.scene_selections
    op.create_table(
        'scene_selections',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('aoi_session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('operational.aoi_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('scene_id', sa.String(255), nullable=False),
        sa.Column('acquisition_datetime', sa.DateTime(timezone=True), nullable=False),
        sa.Column('sensor', sa.String(100), nullable=True),
        sa.Column('collection', sa.String(100), nullable=True),
        sa.Column('rank_score', sa.Float(), nullable=True),
        sa.Column('ranking_provenance', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('selected', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        schema='operational'
    )
    op.create_index('idx_operational_scene_sel_session', 'scene_selections', ['aoi_session_id'], schema='operational')
    op.create_index('idx_operational_scene_sel_scene_id', 'scene_selections', ['scene_id'], schema='operational')

    # 3. operational.analysis_jobs
    op.create_table(
        'analysis_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('aoi_session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('operational.aoi_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('t1_scene_id', sa.String(255), nullable=False),
        sa.Column('t2_scene_id', sa.String(255), nullable=False),
        sa.Column('analysis_run_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('analysis.runs.id', ondelete='SET NULL'), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='PENDING'),
        sa.Column('current_stage', sa.String(100), nullable=False, server_default='INITIALIZED'),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        schema='operational'
    )
    op.create_index('idx_operational_analysis_jobs_session', 'analysis_jobs', ['aoi_session_id'], schema='operational')
    op.create_index('idx_operational_analysis_jobs_status', 'analysis_jobs', ['status'], schema='operational')


def downgrade() -> None:
    op.drop_table('analysis_jobs', schema='operational')
    op.drop_table('scene_selections', schema='operational')
    op.drop_table('aoi_sessions', schema='operational')
    op.execute("DROP SCHEMA IF EXISTS operational CASCADE;")
