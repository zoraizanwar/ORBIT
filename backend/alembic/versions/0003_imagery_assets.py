"""Earth observation imagery assets foundation

Revision ID: 0003_imagery_assets
Revises: 0002_gazetteer_foundation
Create Date: 2026-08-24 01:51:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0003_imagery_assets'
down_revision: Union[str, None] = '0002_gazetteer_foundation'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create eo.imagery_assets Table
    op.create_table(
        'imagery_assets',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('imagery_scene_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('eo.imagery_scenes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('asset_key', sa.String(100), nullable=False),
        sa.Column('href', sa.String(1000), nullable=False),
        sa.Column('media_type', sa.String(100), nullable=True),
        sa.Column('roles', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='[]'),
        sa.Column('title', sa.String(255), nullable=True),
        sa.Column('band_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('gsd', sa.Float(), nullable=True),
        sa.Column('nodata', sa.Float(), nullable=True),
        sa.Column('file_size', sa.BigInteger(), nullable=True),
        sa.Column('checksum', sa.String(128), nullable=True),
        sa.Column('is_cloud_optimized', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        schema='eo',
    )

    op.create_index('idx_assets_scene_id', 'imagery_assets', ['imagery_scene_id'], schema='eo')
    op.create_index('idx_assets_key', 'imagery_assets', ['asset_key'], schema='eo')


def downgrade() -> None:
    op.drop_index('idx_assets_key', table_name='imagery_assets', schema='eo')
    op.drop_index('idx_assets_scene_id', table_name='imagery_assets', schema='eo')
    op.drop_table('imagery_assets', schema='eo')
