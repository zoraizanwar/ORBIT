"""Forecasting foundation and prediction lineage

Revision ID: 0007_forecasting_foundation
Revises: 0006_advanced_geo_intel
Create Date: 2026-08-24 03:15:40.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0007_forecasting_foundation'
down_revision: Union[str, None] = '0006_advanced_geo_intel'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add analysis_run_id and metric columns to history_deep.future_predictions
    op.add_column(
        'future_predictions',
        sa.Column('analysis_run_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('analysis.runs.id', ondelete='SET NULL'), nullable=True),
        schema='history_deep',
    )
    op.add_column(
        'future_predictions',
        sa.Column('metric', sa.String(100), nullable=False, server_default='NDVI'),
        schema='history_deep',
    )
    op.add_column(
        'future_predictions',
        sa.Column('provenance', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        schema='history_deep',
    )
    op.create_index('idx_predictions_analysis_run', 'future_predictions', ['analysis_run_id'], schema='history_deep')
    op.create_index('idx_predictions_metric', 'future_predictions', ['metric'], schema='history_deep')


def downgrade() -> None:
    op.drop_index('idx_predictions_metric', table_name='future_predictions', schema='history_deep')
    op.drop_index('idx_predictions_analysis_run', table_name='future_predictions', schema='history_deep')
    op.drop_column('future_predictions', 'provenance', schema='history_deep')
    op.drop_column('future_predictions', 'metric', schema='history_deep')
    op.drop_column('future_predictions', 'analysis_run_id', schema='history_deep')
