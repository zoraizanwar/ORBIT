import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator
from app.models.enums import SensingModality, EpistemicLevel


class STACSearchRequest(BaseModel):
    collections: Optional[List[str]] = None
    bbox: Optional[List[float]] = Field(
        None,
        description="Bounding box [min_lon, min_lat, max_lon, max_lat] in EPSG:4326",
    )
    intersects: Optional[Dict[str, Any]] = Field(
        None,
        description="GeoJSON Polygon or MultiPolygon geometry in EPSG:4326",
    )
    datetime_start: Optional[datetime] = None
    datetime_end: Optional[datetime] = None
    cloud_cover_max: Optional[float] = Field(
        None,
        ge=0.0,
        le=100.0,
        description="Maximum allowed cloud coverage percentage (0.0 - 100.0)",
    )
    limit: int = Field(20, ge=1, le=100)
    page: int = Field(1, ge=1)
    modality: Optional[str] = Field(
        None,
        description="Filter by modality: OPTICAL_MULTISPECTRAL, SAR_MICROWAVE, HYBRID_FUSION",
    )
    platform: Optional[str] = None
    provider: Optional[str] = None

    @field_validator("bbox")
    @classmethod
    def validate_bbox(cls, v: Optional[List[float]]) -> Optional[List[float]]:
        if v is not None:
            if len(v) != 4:
                raise ValueError("bbox must contain exactly 4 coordinates [min_lon, min_lat, max_lon, max_lat]")
            min_lon, min_lat, max_lon, max_lat = v
            if not (-180.0 <= min_lon <= 180.0 and -180.0 <= max_lon <= 180.0):
                raise ValueError("Longitude coordinates in bbox must be between -180 and 180")
            if not (-90.0 <= min_lat <= 90.0 and -90.0 <= max_lat <= 90.0):
                raise ValueError("Latitude coordinates in bbox must be between -90 and 90")
            if min_lon > max_lon:
                raise ValueError("min_lon cannot be greater than max_lon")
            if min_lat > max_lat:
                raise ValueError("min_lat cannot be greater than max_lat")
        return v

    @field_validator("datetime_end")
    @classmethod
    def validate_datetime_range(cls, v: Optional[datetime], info) -> Optional[datetime]:
        start = info.data.get("datetime_start")
        if start and v and start > v:
            raise ValueError("datetime_start cannot be after datetime_end")
        return v


class NormalizedBand(BaseModel):
    name: str = Field(..., description="Band name/id e.g. B02, B03, B04, B08, VV, VH")
    common_name: Optional[str] = None  # blue, green, red, nir, swir16
    center_wavelength_nm: Optional[float] = None
    full_width_half_max_nm: Optional[float] = None
    polarization: Optional[str] = None  # VV, VH, HH, HV for SAR


class RasterAssetReference(BaseModel):
    asset_key: str = Field(..., description="e.g. B02, B03, B04, B08, VV, VH, visual, thumbnail")
    href: str
    media_type: Optional[str] = None
    roles: List[str] = []
    title: Optional[str] = None
    band: Optional[NormalizedBand] = None
    gsd: Optional[float] = None
    nodata: Optional[float] = None
    file_size_bytes: Optional[int] = None
    checksum: Optional[str] = None
    is_cloud_optimized: bool = True
    access_method: str = "HTTP_RANGE"


class NormalizedImageryScene(BaseModel):
    provider: str = Field(..., description="e.g. Copernicus Data Space, Element84 / AWS Open Data")
    dataset_id: str = Field(..., description="Foreign key to eo.dataset_registry e.g. copernicus-s2-l2a")
    collection_id: str
    item_id: str
    platform: str  # Sentinel-2A, Sentinel-2B, Sentinel-1A, Landsat-9
    sensor: str  # MSI, C-SAR, OLI-2
    modality: SensingModality
    acquisition_datetime: datetime
    processing_datetime: Optional[datetime] = None
    geometry: Dict[str, Any]  # GeoJSON Polygon / MultiPolygon in EPSG:4326
    bbox: List[float]
    cloud_cover: Optional[float] = Field(
        None,
        ge=0.0,
        le=100.0,
        description="Preserves exact cloud cover or null if unavailable (never defaulting to 0.0%)",
    )
    spatial_resolution: float = Field(..., description="GSD in meters (e.g. 10.0, 30.0)")
    processing_level: str  # Level-2A, Level-1C, GRD, Collection 2 Level-2
    bands: List[NormalizedBand] = []
    assets: Dict[str, RasterAssetReference] = {}
    thumbnail_url: Optional[str] = None
    stac_version: str = "1.0.0"
    license: str
    attribution: str
    provider_url: Optional[str] = None
    metadata_payload: Dict[str, Any] = {}
    source_checksum: Optional[str] = None
    epistemic_level: EpistemicLevel = EpistemicLevel.OBSERVED
    geometry_repaired: bool = False


class STACSearchResponse(BaseModel):
    query: STACSearchRequest
    total_matched: int
    returned_count: int
    scenes: List[NormalizedImageryScene]
    providers_contacted: List[str]
    attribution_summary: List[str]


class STACCollectionSummary(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    provider: str
    modality: SensingModality
    temporal_start: Optional[datetime] = None
    temporal_end: Optional[datetime] = None
    license: str
    attribution: str
    spatial_resolution_meters: float
