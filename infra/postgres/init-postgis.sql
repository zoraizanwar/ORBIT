-- ==============================================================================
-- ORBIT PostGIS Initialization Script
-- ==============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "postgis_raster";
CREATE EXTENSION IF NOT EXISTS "btree_gist";

-- Verify PostGIS Version
DO $$
DECLARE
    postgis_ver TEXT;
BEGIN
    SELECT postgis_full_version() INTO postgis_ver;
    RAISE NOTICE 'ORBIT PostGIS successfully initialized: %', postgis_ver;
END $$;
