"""Grounded AI intelligence synthesis and decision support

Revision ID: 0008_grounded_ai_intelligence
Revises: 0007_forecasting_foundation
Create Date: 2026-08-24 03:41:40.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0008_grounded_ai_intelligence'
down_revision: Union[str, None] = '0007_forecasting_foundation'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. intelligence.ai_interpretations
    op.create_table(
        'ai_interpretations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('area_of_interest_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workspace.areas_of_interest.id', ondelete='CASCADE'), nullable=False),
        sa.Column('analysis_run_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('analysis.runs.id', ondelete='SET NULL'), nullable=True),
        sa.Column('intelligence_event_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('intelligence.intelligence_events.id', ondelete='SET NULL'), nullable=True),
        sa.Column('interpretation_type', sa.String(100), nullable=False, server_default='GENERAL_EVALUATION'),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('executive_summary', sa.Text(), nullable=False),
        sa.Column('epistemic_level', sa.String(50), nullable=False, server_default='AI_INTERPRETED'),
        sa.Column('evidence_package_hash', sa.String(64), nullable=False),
        sa.Column('provider_name', sa.String(100), nullable=False, server_default='ORBIT-LocalReasoner'),
        sa.Column('model_name', sa.String(100), nullable=False, server_default='DeterministicGroundedSynthesizer'),
        sa.Column('model_version', sa.String(50), nullable=False, server_default='1.0.0'),
        sa.Column('prompt_version', sa.String(50), nullable=False, server_default='ORBIT-AI-Prompt-v1'),
        sa.Column('uncertainty_statement', sa.Text(), nullable=False),
        sa.Column('contradiction_statement', sa.Text(), nullable=True),
        sa.Column('temporal_interpretation', sa.Text(), nullable=True),
        sa.Column('spatial_interpretation', sa.Text(), nullable=True),
        sa.Column('forecast_interpretation', sa.Text(), nullable=True),
        sa.Column('provenance', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        schema='intelligence',
    )
    op.create_index('idx_ai_interp_aoi', 'ai_interpretations', ['area_of_interest_id'], schema='intelligence')
    op.create_index('idx_ai_interp_type', 'ai_interpretations', ['interpretation_type'], schema='intelligence')
    op.create_index('idx_ai_interp_created', 'ai_interpretations', ['created_at'], schema='intelligence')

    # 2. intelligence.ai_claims
    op.create_table(
        'ai_claims',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('ai_interpretation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('intelligence.ai_interpretations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('claim_text', sa.Text(), nullable=False),
        sa.Column('claim_type', sa.String(50), nullable=False, server_default='INTERPRETATION'),
        sa.Column('epistemic_level', sa.String(50), nullable=False, server_default='AI_INTERPRETED'),
        sa.Column('evidence_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('support_status', sa.String(50), nullable=False, server_default='SUPPORTED'),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='0.95'),
        sa.Column('validation_details', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        schema='intelligence',
    )
    op.create_index('idx_ai_claims_interp', 'ai_claims', ['ai_interpretation_id'], schema='intelligence')
    op.create_index('idx_ai_claims_type', 'ai_claims', ['claim_type'], schema='intelligence')

    # 3. intelligence.ai_recommendations
    op.create_table(
        'ai_recommendations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('ai_interpretation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('intelligence.ai_interpretations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('category', sa.String(50), nullable=False, server_default='MONITOR'),
        sa.Column('recommendation_text', sa.Text(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('priority', sa.String(20), nullable=False, server_default='MEDIUM'),
        sa.Column('supporting_evidence_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('uncertainty_note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        schema='intelligence',
    )
    op.create_index('idx_ai_rec_interp', 'ai_recommendations', ['ai_interpretation_id'], schema='intelligence')
    op.create_index('idx_ai_rec_priority', 'ai_recommendations', ['priority'], schema='intelligence')

    # 4. intelligence.ai_reports
    op.create_table(
        'ai_reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('area_of_interest_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workspace.areas_of_interest.id', ondelete='CASCADE'), nullable=False),
        sa.Column('ai_interpretation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('intelligence.ai_interpretations.id', ondelete='SET NULL'), nullable=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('report_type', sa.String(100), nullable=False, server_default='EXECUTIVE_BRIEF'),
        sa.Column('report_format', sa.String(20), nullable=False, server_default='MARKDOWN'),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('provenance_hash_sha256', sa.String(64), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        schema='intelligence',
    )
    op.create_index('idx_ai_reports_aoi', 'ai_reports', ['area_of_interest_id'], schema='intelligence')
    op.create_index('idx_ai_reports_created', 'ai_reports', ['created_at'], schema='intelligence')


def downgrade() -> None:
    op.drop_table('ai_reports', schema='intelligence')
    op.drop_table('ai_recommendations', schema='intelligence')
    op.drop_table('ai_claims', schema='intelligence')
    op.drop_table('ai_interpretations', schema='intelligence')
