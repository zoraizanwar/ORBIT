"""Raster analysis and measurement indexing foundation

Revision ID: 0004_raster_analysis_foundation
Revises: 0003_imagery_assets
Create Date: 2026-08-24 02:07:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0004_raster_analysis_foundation'
down_revision: Union[str, None] = '0003_imagery_assets'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index('idx_measurements_created_at', 'measurements', ['created_at'], schema='intelligence')
    op.create_index('idx_runs_analysis_type', 'runs', ['analysis_type'], schema='analysis')


def downgrade() -> None:
    op.drop_index('idx_runs_analysis_type', table_name='runs', schema='analysis')
    op.drop_index('idx_measurements_created_at', table_name='measurements', schema='intelligence')
