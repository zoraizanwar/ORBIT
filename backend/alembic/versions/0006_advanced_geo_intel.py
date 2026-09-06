"""Advanced geospatial intelligence and evidence graph foundation

Revision ID: 0006_advanced_geo_intel
Revises: 0005_change_detection_foundation
Create Date: 2026-08-24 02:51:30.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from geoalchemy2 import Geometry

# revision identifiers, used by Alembic.
revision: str = '0006_advanced_geo_intel'
down_revision: Union[str, None] = '0005_change_detection_foundation'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create intelligence.intelligence_events table
    op.create_table(
        'intelligence_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('analysis_run_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('analysis.runs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('area_of_interest_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workspace.areas_of_interest.id', ondelete='SET NULL'), nullable=True),
        sa.Column('intelligence_type', sa.String(100), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('geometry', Geometry(geometry_type='MULTIPOLYGON', srid=4326), nullable=False),
        sa.Column('affected_area', sa.Float(), nullable=False),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('evidence_strength', postgresql.ENUM('STRONG', 'MODERATE', 'LIMITED', 'INSUFFICIENT', name='evidence_strength', schema='intelligence', create_type=False), nullable=False),
        sa.Column('epistemic_level', postgresql.ENUM('OBSERVED', 'CALCULATED', 'DETECTED', 'ESTIMATED', 'PREDICTED', 'AI_INTERPRETATION', name='epistemic_level', schema='intelligence', create_type=False), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('rule_id', sa.String(100), nullable=False),
        sa.Column('rule_version', sa.String(50), nullable=False, server_default='1.0.0'),
        sa.Column('algorithm_version', sa.String(50), nullable=False, server_default='ORBIT-Intelligence-v1.0'),
        sa.Column('quality_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('provenance', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('status', sa.String(50), nullable=False, server_default='ACTIVE'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.CheckConstraint('confidence >= 0.0 AND confidence <= 1.0', name='check_intel_event_confidence_range'),
        sa.CheckConstraint('end_date >= start_date', name='check_intel_event_dates_logical'),
        schema='intelligence',
    )
    op.create_index('idx_intel_events_geometry', 'intelligence_events', ['geometry'], postgresql_using='gist', schema='intelligence')
    op.create_index('idx_intel_events_run_id', 'intelligence_events', ['analysis_run_id'], schema='intelligence')
    op.create_index('idx_intel_events_type', 'intelligence_events', ['intelligence_type'], schema='intelligence')
    op.create_index('idx_intel_events_strength', 'intelligence_events', ['evidence_strength'], schema='intelligence')

    # 2. Add foreign key and columns to intelligence.evidence_records
    op.add_column(
        'evidence_records',
        sa.Column('intelligence_event_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('intelligence.intelligence_events.id', ondelete='SET NULL'), nullable=True),
        schema='intelligence',
    )
    op.add_column(
        'evidence_records',
        sa.Column('epistemic_level', postgresql.ENUM('OBSERVED', 'CALCULATED', 'DETECTED', 'ESTIMATED', 'PREDICTED', 'AI_INTERPRETATION', name='epistemic_level', schema='intelligence', create_type=False), nullable=False, server_default='CALCULATED'),
        schema='intelligence',
    )
    op.create_index('idx_evidence_intel_event_id', 'evidence_records', ['intelligence_event_id'], schema='intelligence')

    # 3. Create intelligence.evidence_relationships table
    op.create_table(
        'evidence_relationships',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('source_evidence_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('intelligence.evidence_records.id', ondelete='CASCADE'), nullable=False),
        sa.Column('target_entity_type', sa.String(50), nullable=False),
        sa.Column('target_entity_id', sa.String(255), nullable=False),
        sa.Column('relationship_type', sa.String(50), nullable=False),
        sa.Column('weight', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('metadata_payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        schema='intelligence',
    )
    op.create_index('idx_rel_source_id', 'evidence_relationships', ['source_evidence_id'], schema='intelligence')
    op.create_index('idx_rel_target_type', 'evidence_relationships', ['target_entity_type'], schema='intelligence')
    op.create_index('idx_rel_type', 'evidence_relationships', ['relationship_type'], schema='intelligence')


def downgrade() -> None:
    op.drop_table('evidence_relationships', schema='intelligence')
    op.drop_index('idx_evidence_intel_event_id', table_name='evidence_records', schema='intelligence')
    op.drop_column('evidence_records', 'epistemic_level', schema='intelligence')
    op.drop_column('evidence_records', 'intelligence_event_id', schema='intelligence')
    op.drop_table('intelligence_events', schema='intelligence')
