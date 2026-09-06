"""Change detection indexing and multi-temporal foundation

Revision ID: 0005_change_detection_foundation
Revises: 0004_raster_analysis_foundation
Create Date: 2026-08-24 02:22:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0005_change_detection_foundation'
down_revision: Union[str, None] = '0004_raster_analysis_foundation'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index('idx_changes_before_date', 'detected_changes', ['before_date'], schema='intelligence')
    op.create_index('idx_changes_after_date', 'detected_changes', ['after_date'], schema='intelligence')
    op.create_index('idx_changes_confidence', 'detected_changes', ['confidence'], schema='intelligence')


def downgrade() -> None:
    op.drop_index('idx_changes_confidence', table_name='detected_changes', schema='intelligence')
    op.drop_index('idx_changes_after_date', table_name='detected_changes', schema='intelligence')
    op.drop_index('idx_changes_before_date', table_name='detected_changes', schema='intelligence')
