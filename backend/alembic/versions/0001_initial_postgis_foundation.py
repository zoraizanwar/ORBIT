"""Initial PostGIS foundation and multi-schema architecture

Revision ID: 0001_postgis_foundation
Revises: 
Create Date: 2026-08-23 07:40:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from geoalchemy2 import Geometry

# revision identifiers, used by Alembic.
revision: str = '0001_postgis_foundation'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create Required Database Schemas
    op.execute("CREATE SCHEMA IF NOT EXISTS auth;")
    op.execute("CREATE SCHEMA IF NOT EXISTS workspace;")
    op.execute("CREATE SCHEMA IF NOT EXISTS geo;")
    op.execute("CREATE SCHEMA IF NOT EXISTS eo;")
    op.execute("CREATE SCHEMA IF NOT EXISTS analysis;")
    op.execute("CREATE SCHEMA IF NOT EXISTS intelligence;")
    op.execute("CREATE SCHEMA IF NOT EXISTS history_deep;")

    # 2. Enable PostGIS & Required Extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
    op.execute('CREATE EXTENSION IF NOT EXISTS "postgis";')
    op.execute('CREATE EXTENSION IF NOT EXISTS "btree_gist";')

    # =========================================================================
    # 3. SCHEMA: auth.users
    # =========================================================================
    user_role_enum = postgresql.ENUM('ANALYST', 'RESEARCHER', 'ADMIN', 'VIEWER', name='user_role', schema='auth', create_type=False)
    user_role_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('role', user_role_enum, nullable=False, server_default='ANALYST'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        schema='auth',
    )
    op.create_index('idx_users_email', 'users', ['email'], schema='auth')

    # =========================================================================
    # 4. SCHEMA: workspace.projects & workspace.areas_of_interest
    # =========================================================================
    project_status_enum = postgresql.ENUM('ACTIVE', 'ARCHIVED', 'COMPLETED', name='project_status', schema='workspace', create_type=False)
    project_status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'projects',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('auth.users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', project_status_enum, nullable=False, server_default='ACTIVE'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        schema='workspace',
    )
    op.create_index('idx_projects_user_id', 'projects', ['user_id'], schema='workspace')

    op.create_table(
        'areas_of_interest',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workspace.projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('geometry', Geometry(geometry_type='MULTIPOLYGON', srid=4326), nullable=False),
        sa.Column('centroid', Geometry(geometry_type='POINT', srid=4326), nullable=True),
        sa.Column('bounding_box', Geometry(geometry_type='POLYGON', srid=4326), nullable=True),
        sa.Column('surface_area_km2', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        schema='workspace',
    )
    op.create_index('idx_aoi_project_id', 'areas_of_interest', ['project_id'], schema='workspace')
    op.create_index('idx_aoi_geometry', 'areas_of_interest', ['geometry'], postgresql_using='gist', schema='workspace')
    op.create_index('idx_aoi_centroid', 'areas_of_interest', ['centroid'], postgresql_using='gist', schema='workspace')
    op.create_index('idx_aoi_bounding_box', 'areas_of_interest', ['bounding_box'], postgresql_using='gist', schema='workspace')

    # =========================================================================
    # 5. SCHEMA: geo.road_features
    # =========================================================================
    op.create_table(
        'road_features',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('osm_id', sa.BigInteger(), nullable=False, unique=True),
        sa.Column('geometry', Geometry(geometry_type='LINESTRING', srid=4326), nullable=False),
        sa.Column('highway_class', sa.String(50), nullable=False),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('ref', sa.String(50), nullable=True),
        sa.Column('surface', sa.String(50), nullable=True),
        sa.Column('lanes', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('maxspeed', sa.Integer(), nullable=True),
        sa.Column('oneway', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('access', sa.String(50), nullable=True),
        sa.Column('bridge', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('tunnel', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('source', sa.String(50), nullable=False, server_default='OpenStreetMap'),
        sa.Column('source_version', sa.String(50), nullable=True),
        sa.Column('length_m', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        schema='geo',
    )
    op.create_index('idx_roads_geometry', 'road_features', ['geometry'], postgresql_using='gist', schema='geo')
    op.create_index('idx_roads_osm_id', 'road_features', ['osm_id'], schema='geo')
    op.create_index('idx_roads_highway_class', 'road_features', ['highway_class'], schema='geo')

    # =========================================================================
    # 6. SCHEMA: eo.dataset_registry & eo.imagery_scenes
    # =========================================================================
    sensing_modality_enum = postgresql.ENUM('OPTICAL', 'SAR', 'DEM', 'VECTOR', 'MULTISPECTRAL', name='sensing_modality', schema='eo', create_type=False)
    sensing_modality_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'dataset_registry',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('provider', sa.String(100), nullable=False),
        sa.Column('dataset_name', sa.String(255), nullable=False),
        sa.Column('dataset_version', sa.String(50), nullable=True),
        sa.Column('modality', sensing_modality_enum, nullable=False, server_default='OPTICAL'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('license', sa.String(100), nullable=False),
        sa.Column('attribution', sa.Text(), nullable=False),
        sa.Column('terms_url', sa.String(500), nullable=True),
        sa.Column('redistribution_allowed', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('commercial_use_allowed', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('api_url', sa.String(500), nullable=True),
        sa.Column('documentation_url', sa.String(500), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        schema='eo',
    )

    op.create_table(
        'imagery_scenes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('dataset_id', sa.String(50), sa.ForeignKey('eo.dataset_registry.id', ondelete='CASCADE'), nullable=False),
        sa.Column('provider_scene_id', sa.String(255), nullable=False, unique=True),
        sa.Column('acquisition_datetime', sa.DateTime(timezone=True), nullable=False),
        sa.Column('platform', sa.String(100), nullable=False),
        sa.Column('sensor', sa.String(100), nullable=False),
        sa.Column('modality', sensing_modality_enum, nullable=False, server_default='OPTICAL'),
        sa.Column('cloud_cover', sa.Float(), nullable=True),
        sa.Column('processing_level', sa.String(50), nullable=False),
        sa.Column('spatial_resolution', sa.Float(), nullable=False),
        sa.Column('geometry', Geometry(geometry_type='POLYGON', srid=4326), nullable=False),
        sa.Column('asset_url', sa.String(1000), nullable=True),
        sa.Column('thumbnail_url', sa.String(1000), nullable=True),
        sa.Column('metadata_payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.CheckConstraint('cloud_cover IS NULL OR (cloud_cover >= 0.0 AND cloud_cover <= 100.0)', name='check_scene_cloud_cover_range'),
        schema='eo',
    )
    op.create_index('idx_scenes_geometry', 'imagery_scenes', ['geometry'], postgresql_using='gist', schema='eo')
    op.create_index('idx_scenes_acquisition_datetime', 'imagery_scenes', ['acquisition_datetime'], schema='eo')
    op.create_index('idx_scenes_dataset_id', 'imagery_scenes', ['dataset_id'], schema='eo')

    # =========================================================================
    # 7. SCHEMA: analysis.runs
    # =========================================================================
    analysis_status_enum = postgresql.ENUM('QUEUED', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED', name='analysis_status', schema='analysis', create_type=False)
    analysis_status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'runs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workspace.projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('area_of_interest_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workspace.areas_of_interest.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', analysis_status_enum, nullable=False, server_default='QUEUED'),
        sa.Column('analysis_type', sa.String(100), nullable=False),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('parameters', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('pipeline_version', sa.String(50), nullable=False, server_default='1.0.0'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.CheckConstraint('end_date >= start_date', name='check_analysis_run_dates'),
        schema='analysis',
    )
    op.create_index('idx_runs_status', 'runs', ['status'], schema='analysis')
    op.create_index('idx_runs_project_id', 'runs', ['project_id'], schema='analysis')
    op.create_index('idx_runs_aoi_id', 'runs', ['area_of_interest_id'], schema='analysis')

    # =========================================================================
    # 8. SCHEMA: intelligence (measurements, changes, events, evidence, reports)
    # =========================================================================
    epistemic_level_enum = postgresql.ENUM('OBSERVED', 'CALCULATED', 'DETECTED', 'ESTIMATED', 'PREDICTED', 'AI_INTERPRETATION', name='epistemic_level', schema='intelligence', create_type=False)
    epistemic_level_enum.create(op.get_bind(), checkfirst=True)

    evidence_strength_enum = postgresql.ENUM('STRONG', 'MODERATE', 'LIMITED', 'INSUFFICIENT', name='evidence_strength', schema='intelligence', create_type=False)
    evidence_strength_enum.create(op.get_bind(), checkfirst=True)

    report_status_enum = postgresql.ENUM('PENDING', 'GENERATING', 'COMPLETED', 'FAILED', name='report_status', schema='intelligence', create_type=False)
    report_status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'measurements',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('analysis_run_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('analysis.runs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('measurement_type', sa.String(100), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(50), nullable=False),
        sa.Column('uncertainty', sa.Float(), nullable=True),
        sa.Column('epistemic_level', epistemic_level_enum, nullable=False, server_default='CALCULATED'),
        sa.Column('methodology', sa.String(255), nullable=False),
        sa.Column('source', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        schema='intelligence',
    )
    op.create_index('idx_measurements_run_id', 'measurements', ['analysis_run_id'], schema='intelligence')
    op.create_index('idx_measurements_type', 'measurements', ['measurement_type'], schema='intelligence')

    op.create_table(
        'detected_changes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('analysis_run_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('analysis.runs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('change_type', sa.String(100), nullable=False),
        sa.Column('geometry', Geometry(geometry_type='MULTIPOLYGON', srid=4326), nullable=False),
        sa.Column('affected_area', sa.Float(), nullable=False),
        sa.Column('percentage_change', sa.Float(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('evidence_strength', evidence_strength_enum, nullable=False, server_default='STRONG'),
        sa.Column('detection_method', sa.String(255), nullable=False),
        sa.Column('before_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('after_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.CheckConstraint('confidence >= 0.0 AND confidence <= 1.0', name='check_change_confidence_range'),
        sa.CheckConstraint('after_date >= before_date', name='check_change_dates_logical'),
        schema='intelligence',
    )
    op.create_index('idx_changes_geometry', 'detected_changes', ['geometry'], postgresql_using='gist', schema='intelligence')
    op.create_index('idx_changes_run_id', 'detected_changes', ['analysis_run_id'], schema='intelligence')
    op.create_index('idx_changes_type', 'detected_changes', ['change_type'], schema='intelligence')

    op.create_table(
        'geographic_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('analysis_run_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('analysis.runs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('geometry', Geometry(geometry_type='MULTIPOLYGON', srid=4326), nullable=False),
        sa.Column('severity', sa.String(50), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('evidence_strength', evidence_strength_enum, nullable=False, server_default='STRONG'),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.CheckConstraint('confidence >= 0.0 AND confidence <= 1.0', name='check_event_confidence_range'),
        sa.CheckConstraint('end_date >= start_date', name='check_event_dates_logical'),
        schema='intelligence',
    )
    op.create_index('idx_events_geometry', 'geographic_events', ['geometry'], postgresql_using='gist', schema='intelligence')
    op.create_index('idx_events_run_id', 'geographic_events', ['analysis_run_id'], schema='intelligence')
    op.create_index('idx_events_type', 'geographic_events', ['event_type'], schema='intelligence')

    op.create_table(
        'evidence_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('analysis_run_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('analysis.runs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source_type', sa.String(100), nullable=False),
        sa.Column('source_id', sa.String(255), nullable=False),
        sa.Column('claim_type', sa.String(100), nullable=False),
        sa.Column('claim_reference', sa.String(255), nullable=False),
        sa.Column('input_checksum', sa.String(64), nullable=False),
        sa.Column('processing_version', sa.String(50), nullable=False, server_default='ORBIT-Engine-v1.0.0'),
        sa.Column('algorithm', sa.String(100), nullable=False),
        sa.Column('parameters', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('evidence_strength', evidence_strength_enum, nullable=False, server_default='STRONG'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        schema='intelligence',
    )
    op.create_index('idx_evidence_run_id', 'evidence_records', ['analysis_run_id'], schema='intelligence')
    op.create_index('idx_evidence_source_id', 'evidence_records', ['source_id'], schema='intelligence')
    op.create_index('idx_evidence_checksum', 'evidence_records', ['input_checksum'], schema='intelligence')

    op.create_table(
        'reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('analysis_run_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('analysis.runs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('report_type', sa.String(100), nullable=False, server_default='EXECUTIVE_INTELLIGENCE_DOSSIER'),
        sa.Column('status', report_status_enum, nullable=False, server_default='PENDING'),
        sa.Column('executive_summary', sa.Text(), nullable=True),
        sa.Column('file_path', sa.String(1000), nullable=True),
        sa.Column('methodology_version', sa.String(50), nullable=False, server_default='1.0.0'),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        schema='intelligence',
    )
    op.create_index('idx_reports_run_id', 'reports', ['analysis_run_id'], schema='intelligence')
    op.create_index('idx_reports_status', 'reports', ['status'], schema='intelligence')

    # =========================================================================
    # 9. SCHEMA: history_deep (historical annual, predictions, geological, islamic)
    # =========================================================================
    support_classification_enum = postgresql.ENUM('STRONGLY_SUPPORTED', 'PARTIALLY_SUPPORTED', 'ESTIMATED', 'UNAVAILABLE', name='support_classification', schema='history_deep', create_type=False)
    support_classification_enum.create(op.get_bind(), checkfirst=True)

    future_prediction_type_enum = postgresql.ENUM('URBAN_EXPANSION', 'VEGETATION_TREND', 'WATER_COVERAGE', 'ROAD_DEVELOPMENT', 'LAND_USE_CHANGE', name='future_prediction_type', schema='history_deep', create_type=False)
    future_prediction_type_enum.create(op.get_bind(), checkfirst=True)

    islamic_source_grade_enum = postgresql.ENUM('QURAN', 'MUTAWATIR_HADITH', 'AHAD_SAHIH', 'SCHOLARLY_IJMA', 'HISTORICAL_TARIKH', 'UNVERIFIED_ISRAILIYYAT', name='islamic_source_grade', schema='history_deep', create_type=False)
    islamic_source_grade_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'historical_annual_summaries',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('area_of_interest_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workspace.areas_of_interest.id', ondelete='CASCADE'), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('support_classification', support_classification_enum, nullable=False, server_default='STRONGLY_SUPPORTED'),
        sa.Column('summary_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('data_sources', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.UniqueConstraint('area_of_interest_id', 'year', name='uq_aoi_historical_year'),
        schema='history_deep',
    )
    op.create_index('idx_historical_aoi_year', 'historical_annual_summaries', ['area_of_interest_id', 'year'], schema='history_deep')
    op.create_index('idx_historical_support', 'historical_annual_summaries', ['support_classification'], schema='history_deep')

    op.create_table(
        'future_predictions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('area_of_interest_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workspace.areas_of_interest.id', ondelete='CASCADE'), nullable=False),
        sa.Column('prediction_type', future_prediction_type_enum, nullable=False),
        sa.Column('target_year', sa.Integer(), nullable=False),
        sa.Column('prediction_value', sa.Float(), nullable=False),
        sa.Column('lower_bound', sa.Float(), nullable=True),
        sa.Column('upper_bound', sa.Float(), nullable=True),
        sa.Column('unit', sa.String(50), nullable=False),
        sa.Column('model_name', sa.String(100), nullable=False),
        sa.Column('model_version', sa.String(50), nullable=False, server_default='1.0.0'),
        sa.Column('training_start_year', sa.Integer(), nullable=False),
        sa.Column('training_end_year', sa.Integer(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='0.8'),
        sa.Column('evidence_strength', evidence_strength_enum, nullable=False, server_default='MODERATE'),
        sa.Column('scenario', sa.String(100), nullable=False, server_default='BUSINESS_AS_USUAL'),
        sa.Column('assumptions', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('limitations', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.CheckConstraint('target_year > training_end_year', name='check_prediction_target_after_training'),
        sa.CheckConstraint('training_end_year >= training_start_year', name='check_prediction_training_years'),
        sa.CheckConstraint('confidence >= 0.0 AND confidence <= 1.0', name='check_prediction_confidence_range'),
        sa.CheckConstraint('upper_bound IS NULL OR lower_bound IS NULL OR upper_bound >= lower_bound', name='check_prediction_bounds_logical'),
        schema='history_deep',
    )
    op.create_index('idx_predictions_aoi_target', 'future_predictions', ['area_of_interest_id', 'target_year'], schema='history_deep')
    op.create_index('idx_predictions_type', 'future_predictions', ['prediction_type'], schema='history_deep')

    op.create_table(
        'geological_epochs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('start_age', sa.Float(), nullable=False),
        sa.Column('end_age', sa.Float(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('evidence_type', sa.String(100), nullable=False),
        sa.Column('source', sa.String(255), nullable=False, server_default='International Commission on Stratigraphy (ICS)'),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.CheckConstraint('start_age >= end_age', name='check_geological_age_order'),
        schema='history_deep',
    )

    op.create_table(
        'islamic_geographic_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('source_type', sa.String(100), nullable=False),
        sa.Column('classification', islamic_source_grade_enum, nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('date_reference', sa.String(100), nullable=True),
        sa.Column('geographic_reference', sa.String(255), nullable=False),
        sa.Column('geometry', Geometry(geometry_type='GEOMETRY', srid=4326), nullable=True),
        sa.Column('source', sa.String(500), nullable=False),
        sa.Column('source_url', sa.String(500), nullable=True),
        sa.Column('scholarly_notes', sa.Text(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.CheckConstraint('confidence >= 0.0 AND confidence <= 1.0', name='check_islamic_record_confidence_range'),
        schema='history_deep',
    )
    op.create_index('idx_islamic_geo_geometry', 'islamic_geographic_records', ['geometry'], postgresql_using='gist', schema='history_deep')
    op.create_index('idx_islamic_classification', 'islamic_geographic_records', ['classification'], schema='history_deep')


def downgrade() -> None:
    # Drop Tables in Reverse Dependency Order
    op.drop_table('islamic_geographic_records', schema='history_deep')
    op.drop_table('geological_epochs', schema='history_deep')
    op.drop_table('future_predictions', schema='history_deep')
    op.drop_table('historical_annual_summaries', schema='history_deep')
    op.drop_table('reports', schema='intelligence')
    op.drop_table('evidence_records', schema='intelligence')
    op.drop_table('geographic_events', schema='intelligence')
    op.drop_table('detected_changes', schema='intelligence')
    op.drop_table('measurements', schema='intelligence')
    op.drop_table('runs', schema='analysis')
    op.drop_table('imagery_scenes', schema='eo')
    op.drop_table('dataset_registry', schema='eo')
    op.drop_table('road_features', schema='geo')
    op.drop_table('areas_of_interest', schema='workspace')
    op.drop_table('projects', schema='workspace')
    op.drop_table('users', schema='auth')

    # Drop Enums
    islamic_source_grade_enum = postgresql.ENUM('QURAN', 'MUTAWATIR_HADITH', 'AHAD_SAHIH', 'SCHOLARLY_IJMA', 'HISTORICAL_TARIKH', 'UNVERIFIED_ISRAILIYYAT', name='islamic_source_grade', schema='history_deep')
    islamic_source_grade_enum.drop(op.get_bind(), checkfirst=True)

    future_prediction_type_enum = postgresql.ENUM('URBAN_EXPANSION', 'VEGETATION_TREND', 'WATER_COVERAGE', 'ROAD_DEVELOPMENT', 'LAND_USE_CHANGE', name='future_prediction_type', schema='history_deep')
    future_prediction_type_enum.drop(op.get_bind(), checkfirst=True)

    support_classification_enum = postgresql.ENUM('STRONGLY_SUPPORTED', 'PARTIALLY_SUPPORTED', 'ESTIMATED', 'UNAVAILABLE', name='support_classification', schema='history_deep')
    support_classification_enum.drop(op.get_bind(), checkfirst=True)

    report_status_enum = postgresql.ENUM('PENDING', 'GENERATING', 'COMPLETED', 'FAILED', name='report_status', schema='intelligence')
    report_status_enum.drop(op.get_bind(), checkfirst=True)

    evidence_strength_enum = postgresql.ENUM('STRONG', 'MODERATE', 'LIMITED', 'INSUFFICIENT', name='evidence_strength', schema='intelligence')
    evidence_strength_enum.drop(op.get_bind(), checkfirst=True)

    epistemic_level_enum = postgresql.ENUM('OBSERVED', 'CALCULATED', 'DETECTED', 'ESTIMATED', 'PREDICTED', 'AI_INTERPRETATION', name='epistemic_level', schema='intelligence')
    epistemic_level_enum.drop(op.get_bind(), checkfirst=True)

    analysis_status_enum = postgresql.ENUM('QUEUED', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED', name='analysis_status', schema='analysis')
    analysis_status_enum.drop(op.get_bind(), checkfirst=True)

    sensing_modality_enum = postgresql.ENUM('OPTICAL', 'SAR', 'DEM', 'VECTOR', 'MULTISPECTRAL', name='sensing_modality', schema='eo')
    sensing_modality_enum.drop(op.get_bind(), checkfirst=True)

    project_status_enum = postgresql.ENUM('ACTIVE', 'ARCHIVED', 'COMPLETED', name='project_status', schema='workspace')
    project_status_enum.drop(op.get_bind(), checkfirst=True)

    user_role_enum = postgresql.ENUM('ANALYST', 'RESEARCHER', 'ADMIN', 'VIEWER', name='user_role', schema='auth')
    user_role_enum.drop(op.get_bind(), checkfirst=True)

    # Drop Schemas
    op.execute('DROP SCHEMA IF EXISTS history_deep CASCADE;')
    op.execute('DROP SCHEMA IF EXISTS intelligence CASCADE;')
    op.execute('DROP SCHEMA IF EXISTS analysis CASCADE;')
    op.execute('DROP SCHEMA IF EXISTS eo CASCADE;')
    op.execute('DROP SCHEMA IF EXISTS geo CASCADE;')
    op.execute('DROP SCHEMA IF EXISTS workspace CASCADE;')
    op.execute('DROP SCHEMA IF EXISTS auth CASCADE;')
