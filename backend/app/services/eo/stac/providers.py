import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional
import httpx

from app.core.config import settings
from app.core.logging import logger
from app.models.enums import SensingModality
from app.services.eo.stac.exceptions import (
    STACProviderError,
    STACTimeoutError,
    STACInvalidResponseError,
    STACAuthenticationError,
    STACRateLimitError,
)
from app.services.eo.stac.models import (
    STACSearchRequest,
    STACSearchResponse,
    NormalizedImageryScene,
    STACCollectionSummary,
)
from app.services.eo.stac.parser import parse_stac_item


class STACProvider(ABC):
    """
    Abstract interface for Open STAC API providers.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable provider name."""
        pass

    @property
    @abstractmethod
    def base_url(self) -> str:
        """Base STAC API endpoint URL."""
        pass

    @property
    @abstractmethod
    def supported_collections(self) -> List[str]:
        """List of supported collection IDs."""
        pass

    @abstractmethod
    async def search(self, request: STACSearchRequest) -> STACSearchResponse:
        """Executes a STAC search request and returns normalized scenes."""
        pass

    @abstractmethod
    async def get_item(self, collection_id: str, item_id: str) -> Optional[NormalizedImageryScene]:
        """Retrieves a single STAC item by ID."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Checks remote STAC provider availability."""
        pass


class BaseSTACProvider(STACProvider):
    """
    Generic implementation of STAC 1.0.0 API client with bounded retry and error mapping.
    """

    def __init__(
        self,
        name: str,
        base_url: str,
        supported_collections: Optional[List[str]] = None,
        timeout_seconds: Optional[int] = None,
        max_retries: Optional[int] = None,
    ):
        self._name = name
        self._base_url = base_url.rstrip("/")
        self._supported_collections = supported_collections or []
        self._timeout = timeout_seconds or settings.STAC_REQUEST_TIMEOUT_SECONDS
        self._max_retries = max_retries or settings.STAC_MAX_RETRIES

    @property
    def name(self) -> str:
        return self._name

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def supported_collections(self) -> List[str]:
        return self._supported_collections

    def _build_stac_search_payload(self, request: STACSearchRequest) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "limit": min(request.limit, 100),
        }

        # Collections filter
        target_collections = request.collections or self.supported_collections
        if target_collections:
            payload["collections"] = target_collections

        # Bounding box or Intersects geometry
        if request.intersects:
            payload["intersects"] = request.intersects
        elif request.bbox:
            payload["bbox"] = request.bbox

        # Datetime range
        if request.datetime_start and request.datetime_end:
            start_iso = request.datetime_start.strftime("%Y-%m-%dT%H:%M:%SZ")
            end_iso = request.datetime_end.strftime("%Y-%m-%dT%H:%M:%SZ")
            payload["datetime"] = f"{start_iso}/{end_iso}"
        elif request.datetime_start:
            start_iso = request.datetime_start.strftime("%Y-%m-%dT%H:%M:%SZ")
            payload["datetime"] = f"{start_iso}/.."
        elif request.datetime_end:
            end_iso = request.datetime_end.strftime("%Y-%m-%dT%H:%M:%SZ")
            payload["datetime"] = f"../{end_iso}"

        # Cloud cover query filter (Standard STAC extension eo:cloud_cover)
        if request.cloud_cover_max is not None:
            payload["query"] = {
                "eo:cloud_cover": {"lte": request.cloud_cover_max}
            }

        return payload

    async def _post_with_retry(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self._base_url}/{endpoint.lstrip('/')}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/geo+json, application/json",
        }

        last_exc: Optional[Exception] = None
        for attempt in range(self._max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self._timeout) as client:
                    resp = await client.post(url, json=payload, headers=headers)

                    if resp.status_code == 200:
                        return resp.json()
                    elif resp.status_code == 401 or resp.status_code == 403:
                        raise STACAuthenticationError(f"Provider {self.name} authentication failed: HTTP {resp.status_code}")
                    elif resp.status_code == 429:
                        raise STACRateLimitError(f"Provider {self.name} rate limit exceeded: HTTP 429")
                    elif 400 <= resp.status_code < 500:
                        raise STACProviderError(f"Provider {self.name} rejected request: HTTP {resp.status_code} - {resp.text[:200]}")
                    elif resp.status_code >= 500:
                        # Transient server error: trigger retry
                        last_exc = STACProviderError(f"Provider {self.name} internal error: HTTP {resp.status_code}")
            except httpx.TimeoutException as e:
                last_exc = STACTimeoutError(f"Provider {self.name} timed out after {self._timeout}s: {str(e)}")
            except httpx.NetworkError as e:
                last_exc = STACProviderError(f"Provider {self.name} network error: {str(e)}")

            # Exponential backoff for transient retries
            if attempt < self._max_retries:
                backoff_sec = 0.5 * (2 ** attempt)
                logger.warning(f"STAC provider {self.name} call failed, retrying in {backoff_sec}s (attempt {attempt + 1}/{self._max_retries})...")
                await asyncio.sleep(backoff_sec)

        if last_exc:
            raise last_exc
        raise STACProviderError(f"Provider {self.name} failed after {self._max_retries} attempts")

    async def search(self, request: STACSearchRequest) -> STACSearchResponse:
        payload = self._build_stac_search_payload(request)
        try:
            raw_response = await self._post_with_retry("search", payload)
        except Exception as e:
            logger.error(f"STAC search error on provider {self.name}: {str(e)}")
            return STACSearchResponse(
                query=request,
                total_matched=0,
                returned_count=0,
                scenes=[],
                providers_contacted=[self.name],
                attribution_summary=[],
            )

        features = raw_response.get("features", [])
        scenes: List[NormalizedImageryScene] = []
        attributions: set = set()

        for feat in features:
            try:
                scene = parse_stac_item(feat, provider_name=self.name)
                # Client-side filtering check for cloud cover if provider query was loose
                if request.cloud_cover_max is not None and scene.cloud_cover is not None:
                    if scene.cloud_cover > request.cloud_cover_max:
                        continue
                scenes.append(scene)
                attributions.add(scene.attribution)
            except Exception as parse_err:
                logger.warning(f"Skipping invalid STAC item from {self.name}: {str(parse_err)}")

        total_matched = raw_response.get("numberMatched") or len(scenes)

        return STACSearchResponse(
            query=request,
            total_matched=total_matched,
            returned_count=len(scenes),
            scenes=scenes,
            providers_contacted=[self.name],
            attribution_summary=list(attributions),
        )

    async def get_item(self, collection_id: str, item_id: str) -> Optional[NormalizedImageryScene]:
        url = f"{self._base_url}/collections/{collection_id}/items/{item_id}"
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    return parse_stac_item(resp.json(), provider_name=self.name)
                elif resp.status_code == 404:
                    return None
                else:
                    raise STACProviderError(f"Failed to fetch STAC item {item_id}: HTTP {resp.status_code}")
        except Exception as e:
            logger.error(f"Error fetching STAC item {item_id} from {self.name}: {str(e)}")
            return None

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(self._base_url)
                return resp.status_code in [200, 204]
        except Exception:
            return False


# =============================================================================
# Preconfigured Provider Singletons
# =============================================================================

class EarthSearchAWSProvider(BaseSTACProvider):
    def __init__(self):
        super().__init__(
            name="Element84 Earth Search (AWS Open Data)",
            base_url=settings.STAC_EARTH_SEARCH_URL,
            supported_collections=["sentinel-2-l2a", "sentinel-2-c1-l2a", "landsat-c2-l2"],
        )


class CopernicusDataSpaceProvider(BaseSTACProvider):
    def __init__(self):
        super().__init__(
            name="Copernicus Data Space Ecosystem (CDSE)",
            base_url=settings.STAC_COPERNICUS_URL,
            supported_collections=["SENTINEL-2", "SENTINEL-1"],
        )


class PlanetaryComputerProvider(BaseSTACProvider):
    def __init__(self):
        super().__init__(
            name="Microsoft Planetary Computer",
            base_url=settings.STAC_PLANETARY_COMPUTER_URL,
            supported_collections=["sentinel-2-l2a", "sentinel-1-grd", "landsat-c2-l2"],
        )
