from datetime import datetime
from typing import Any, Dict, List, Optional
from app.services.eo.stac.models import NormalizedImageryScene
from app.services.eo.stac.real_discovery import (
    DeterministicSceneRanker,
    SceneRankingCriteria,
    RankedImageryScene,
)


class SceneSelectionService:
    """
    Deterministic STAC Scene Selection & Ranking Orchestration Service.
    Wraps Phase 15 DeterministicSceneRanker to evaluate multi-criteria suitability,
    returning stable, reproducible rank scores and provenance metadata.
    """

    @classmethod
    def rank_candidate_scenes(
        cls,
        candidate_scenes: List[NormalizedImageryScene],
        target_aoi_bbox: List[float],
        target_datetime: Optional[datetime] = None,
        criteria: Optional[SceneRankingCriteria] = None,
    ) -> List[RankedImageryScene]:
        """
        Executes deterministic multi-criteria scene ranking across supplied scenes.
        """
        return DeterministicSceneRanker.rank_scenes(
            scenes=candidate_scenes,
            target_datetime=target_datetime,
            aoi_bbox=target_aoi_bbox,
            criteria=criteria,
        )
