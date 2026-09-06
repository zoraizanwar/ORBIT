from typing import Dict, List, Optional, Any
from app.services.eo.stac.models import (
    STACSearchRequest,
    STACSearchResponse,
    NormalizedImageryScene,
    STACCollectionSummary,
)
from app.services.eo.stac.providers import (
    STACProvider,
    EarthSearchAWSProvider,
    CopernicusDataSpaceProvider,
    PlanetaryComputerProvider,
)


class STACClientManager:
    """
    Orchestrates multiple STAC API providers with fallback and federated discovery.
    """

    def __init__(self):
        self._providers: Dict[str, STACProvider] = {
            "earth-search": EarthSearchAWSProvider(),
            "copernicus": CopernicusDataSpaceProvider(),
            "planetary-computer": PlanetaryComputerProvider(),
        }

    def get_provider(self, key: str) -> Optional[STACProvider]:
        return self._providers.get(key)

    def list_providers(self) -> List[Dict[str, Any]]:
        return [
            {
                "key": k,
                "name": p.name,
                "base_url": p.base_url,
                "supported_collections": p.supported_collections,
            }
            for k, p in self._providers.items()
        ]

    async def search(self, request: STACSearchRequest) -> STACSearchResponse:
        """
        Executes search on specified provider or federates across available providers.
        """
        if request.provider and request.provider in self._providers:
            provider = self._providers[request.provider]
            return await provider.search(request)

        # Primary default provider: Earth Search (Element84 / AWS Open Data)
        primary = self._providers["earth-search"]
        resp = await primary.search(request)

        if resp.returned_count > 0:
            return resp

        # Fallback to secondary if primary returned 0 results and no specific provider requested
        secondary = self._providers["planetary-computer"]
        resp_sec = await secondary.search(request)
        return resp_sec


# Global manager instance
stac_client_manager = STACClientManager()
