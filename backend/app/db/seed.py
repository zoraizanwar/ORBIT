import asyncio
from typing import List, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.models.eo.dataset_registry import DatasetRegistry
from app.models.enums import SensingModality
from app.core.logging import logger

# Official Dataset Registry Metadata Seeds
SEED_DATASETS: List[Dict[str, Any]] = [
    {
        "id": "copernicus-s2-l2a",
        "provider": "European Space Agency (ESA) / Copernicus",
        "dataset_name": "Sentinel-2 MSI Level-2A (Surface Reflectance)",
        "dataset_version": "Collection-1",
        "modality": SensingModality.OPTICAL,
        "description": "Multi-spectral optical telemetry with 13 bands (10m VIS/NIR, 20m SWIR, 60m atmospheric). Calibrated to bottom-of-atmosphere surface reflectance.",
        "license": "EU Copernicus Open Access Policy (Regulation EU 377/2014)",
        "attribution": "Contains modified Copernicus Sentinel data [Year] processed by ORBIT",
        "terms_url": "https://dataspace.copernicus.eu/terms-and-conditions",
        "redistribution_allowed": True,
        "commercial_use_allowed": True,
        "api_url": "https://catalogue.dataspace.copernicus.eu/stac",
        "documentation_url": "https://sentinels.copernicus.eu/web/sentinel/user-guides/sentinel-2-msi",
        "active": True,
    },
    {
        "id": "copernicus-s1-grd",
        "provider": "European Space Agency (ESA) / Copernicus",
        "dataset_name": "Sentinel-1 SAR C-Band Ground Range Detected (GRD)",
        "dataset_version": "Level-1",
        "modality": SensingModality.SAR,
        "description": "Active microwave C-band synthetic aperture radar (5.405 GHz) providing all-weather, day-and-night surface roughness, moisture, and structural coherence observations at 10m resolution.",
        "license": "EU Copernicus Open Access Policy (Regulation EU 377/2014)",
        "attribution": "Contains modified Copernicus Sentinel data [Year] processed by ORBIT",
        "terms_url": "https://dataspace.copernicus.eu/terms-and-conditions",
        "redistribution_allowed": True,
        "commercial_use_allowed": True,
        "api_url": "https://catalogue.dataspace.copernicus.eu/stac",
        "documentation_url": "https://sentinels.copernicus.eu/web/sentinel/user-guides/sentinel-1-sar",
        "active": True,
    },
    {
        "id": "usgs-landsat-c2l2",
        "provider": "U.S. Geological Survey (USGS) / NASA",
        "dataset_name": "Landsat 4-9 Collection 2 Level-2 (Surface Reflectance)",
        "dataset_version": "Collection-2 Tier-1",
        "modality": SensingModality.OPTICAL,
        "description": "Continuous 50+ year multispectral Earth observation archive (1972-Present) across Landsat MSS, TM, ETM+, and OLI sensors at 30m resolution for multi-decadal historical intelligence.",
        "license": "Public Domain (U.S. Government Work)",
        "attribution": "Landsat data courtesy of the U.S. Geological Survey",
        "terms_url": "https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits",
        "redistribution_allowed": True,
        "commercial_use_allowed": True,
        "api_url": "https://landsatlook.usgs.gov/stac-server",
        "documentation_url": "https://www.usgs.gov/landsat-missions/landsat-collection-2",
        "active": True,
    },
    {
        "id": "copernicus-dem-30",
        "provider": "Copernicus / DLR / Airbus Defence and Space",
        "dataset_name": "Copernicus Digital Elevation Model (GLO-30)",
        "dataset_version": "GLO-30 Public",
        "modality": SensingModality.DEM,
        "description": "Global digital surface elevation model at 30m spatial resolution derived from WorldDEM radar interferometry, essential for terrain slope and hydrological drainage analysis.",
        "license": "Copernicus DEM Open Policy",
        "attribution": "Copernicus DEM data © DLR, Airbus Defence & Space, ESA [Year]",
        "terms_url": "https://spacedata.copernicus.eu/collections/copernicus-digital-elevation-model",
        "redistribution_allowed": True,
        "commercial_use_allowed": True,
        "api_url": "https://planetarycomputer.microsoft.com/api/stac/v1",
        "documentation_url": "https://spacedata.copernicus.eu/web/cscda/data-offer",
        "active": True,
    },
    {
        "id": "osm-roads-planet",
        "provider": "OpenStreetMap Foundation (OSMF)",
        "dataset_name": "OpenStreetMap Global Road & Infrastructure Topology",
        "dataset_version": "Planet PBF Extract",
        "modality": SensingModality.VECTOR,
        "description": "Worldwide mapped road network, street hierarchy, surfaces, bridges, tunnels, and infrastructure vectors.",
        "license": "Open Database License (ODbL 1.0)",
        "attribution": "© OpenStreetMap contributors",
        "terms_url": "https://www.openstreetmap.org/copyright",
        "redistribution_allowed": True,
        "commercial_use_allowed": True,
        "api_url": "https://download.geofabrik.de",
        "documentation_url": "https://wiki.openstreetmap.org/wiki/Key:highway",
        "active": True,
    },
    {
        "id": "hydrosheds-v1",
        "provider": "World Wildlife Fund (WWF) / HydroSHEDS",
        "dataset_name": "HydroSHEDS Global Hydrography & River Basins",
        "dataset_version": "v1.0",
        "modality": SensingModality.VECTOR,
        "description": "Global vector drainage network, river flow directions, and lake basin polygons derived from SRTM elevation data.",
        "license": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
        "attribution": "HydroSHEDS database © World Wildlife Fund, Inc.",
        "terms_url": "https://www.hydrosheds.org/license",
        "redistribution_allowed": True,
        "commercial_use_allowed": True,
        "api_url": "https://www.hydrosheds.org",
        "documentation_url": "https://www.hydrosheds.org/page/overview",
        "active": True,
    },
]


async def seed_dataset_registry(db: AsyncSession) -> int:
    """Seeds the eo.dataset_registry table with reference open metadata."""
    seeded_count = 0
    for ds_data in SEED_DATASETS:
        stmt = select(DatasetRegistry).where(DatasetRegistry.id == ds_data["id"])
        existing = (await db.execute(stmt)).scalar_one_or_none()
        if not existing:
            new_record = DatasetRegistry(**ds_data)
            db.add(new_record)
            seeded_count += 1
            logger.info(f"Seeding dataset registry entry: {ds_data['id']}")
        else:
            logger.debug(f"Dataset registry entry already exists: {ds_data['id']}")
    
    await db.commit()
    return seeded_count


async def run_seeds():
    """Main seed entry point."""
    logger.info("Starting ORBIT database reference metadata seeding...")
    async with AsyncSessionLocal() as session:
        count = await seed_dataset_registry(session)
        logger.info(f"Seeding completed successfully. {count} new datasets added.")


if __name__ == "__main__":
    asyncio.run(run_seeds())
