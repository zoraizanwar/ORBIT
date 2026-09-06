from typing import Any, Dict, List, Optional
from datetime import datetime
from app.services.eo.stac.models import (
    STACSearchRequest,
    STACSearchResponse,
    NormalizedImageryScene,
)
from app.services.eo.discovery.scene_discovery import execute_scene_discovery
from app.services.eo.operational.models import OperationalSceneSearchRequest


class STACDiscoveryService:
    """
    Live Earth Observation STAC Scene Discovery Service.
    Queries configured real STAC APIs (Earth Search / Copernicus Data Space),
    filters by AOI bounding box, temporal range, cloud percentage, and platform.
    Never fabricates satellite metadata.
    """

    @classmethod
    async def search_scenes(
        cls,
        req: OperationalSceneSearchRequest,
        bbox_override: Optional[List[float]] = None,
    ) -> STACSearchResponse:
        """
        Executes normalized STAC query against live providers with graceful offline fallbacks.
        """
        target_bbox = bbox_override or req.bbox
        
        # Build normalized STACSearchRequest
        search_req = STACSearchRequest(
            bbox=tuple(target_bbox) if target_bbox and len(target_bbox) == 4 else None,
            datetime_start=datetime.fromisoformat(req.datetime_start.replace("Z", "+00:00")) if req.datetime_start else None,
            datetime_end=datetime.fromisoformat(req.datetime_end.replace("Z", "+00:00")) if req.datetime_end else None,
            cloud_cover_max=req.cloud_cover_max,
            platform=req.platform,
            limit=req.limit,
        )

        response = await execute_scene_discovery(search_req)
        return response

