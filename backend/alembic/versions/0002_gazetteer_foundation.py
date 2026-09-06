"""Gazetteer entities foundation and spatial search indexes

Revision ID: 0002_gazetteer_foundation
Revises: 0001_postgis_foundation
Create Date: 2026-08-24 01:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from geoalchemy2 import Geometry

# revision identifiers, used by Alembic.
revision: str = '0002_gazetteer_foundation'
down_revision: Union[str, None] = '0001_postgis_foundation'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Enable pg_trgm for fast trigram/fuzzy text matching if available
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm";')

    # 2. Create geo.gazetteer_entities Table
    op.create_table(
        'gazetteer_entities',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('provider', sa.String(50), nullable=False, server_default='OpenStreetMap'),
        sa.Column('provider_entity_id', sa.String(100), nullable=True),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('normalized_name', sa.String(255), nullable=False),
        sa.Column('alternate_names', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='[]'),
        sa.Column('country_code', sa.String(10), nullable=True),
        sa.Column('country_name', sa.String(100), nullable=True),
        sa.Column('admin_level_1', sa.String(100), nullable=True),
        sa.Column('admin_level_2', sa.String(100), nullable=True),
        sa.Column('admin_level_3', sa.String(100), nullable=True),
        sa.Column('population', sa.BigInteger(), nullable=True),
        sa.Column('geometry', Geometry(geometry_type='GEOMETRY', srid=4326, spatial_index=False), nullable=True),
        sa.Column('centroid', Geometry(geometry_type='POINT', srid=4326, spatial_index=False), nullable=False),
        sa.Column('bounding_box', Geometry(geometry_type='POLYGON', srid=4326, spatial_index=False), nullable=True),
        sa.Column('metadata_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('source_version', sa.String(50), nullable=True),
        sa.Column('is_searchable', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        schema='geo',
    )

    # 3. Create Spatial and Text Search Indexes
    op.create_index('idx_gazetteer_centroid', 'gazetteer_entities', ['centroid'], postgresql_using='gist', schema='geo')
    op.create_index('idx_gazetteer_geometry', 'gazetteer_entities', ['geometry'], postgresql_using='gist', schema='geo')
    op.create_index('idx_gazetteer_normalized_name', 'gazetteer_entities', ['normalized_name'], schema='geo')
    op.create_index('idx_gazetteer_country_code', 'gazetteer_entities', ['country_code'], schema='geo')
    op.create_index('idx_gazetteer_entity_type', 'gazetteer_entities', ['entity_type'], schema='geo')
    op.create_index('idx_gazetteer_provider_entity_id', 'gazetteer_entities', ['provider_entity_id'], schema='geo')


def downgrade() -> None:
    op.drop_index('idx_gazetteer_provider_entity_id', table_name='gazetteer_entities', schema='geo')
    op.drop_index('idx_gazetteer_entity_type', table_name='gazetteer_entities', schema='geo')
    op.drop_index('idx_gazetteer_country_code', table_name='gazetteer_entities', schema='geo')
    op.drop_index('idx_gazetteer_normalized_name', table_name='gazetteer_entities', schema='geo')
    op.drop_index('idx_gazetteer_geometry', table_name='gazetteer_entities', schema='geo')
    op.drop_index('idx_gazetteer_centroid', table_name='gazetteer_entities', schema='geo')
    op.drop_table('gazetteer_entities', schema='geo')
