import uuid
from datetime import datetime, timezone
import pytest
from app.models.enums import EpistemicLevel, SensingModality, FuturePredictionType, EvidenceStrength
from app.models.history_deep.future_prediction import FuturePrediction
from app.services.eo.stac.models import NormalizedImageryScene


def test_imagery_scene_epistemic_classification_invariants():
    """
    Satellite scenes discovered from STAC catalogs are strictly OBSERVED external telemetry.
    They cannot be tagged as PREDICTED or DETECTED.
    """
    scene = NormalizedImageryScene(
        provider="Copernicus CDSE",
        dataset_id="copernicus-s2-l2a",
        collection_id="sentinel-2-l2a",
        item_id="S2B_TEST_SCENE",
        platform="Sentinel-2B",
        sensor="MSI",
        modality=SensingModality.OPTICAL,
        acquisition_datetime=datetime(2026, 8, 20, 12, 0, 0, tzinfo=timezone.utc),
        geometry={"type": "Polygon", "coordinates": [[[-55, -12], [-54, -12], [-54, -11], [-55, -11], [-55, -12]]]},
        bbox=[-55.0, -12.0, -54.0, -11.0],
        cloud_cover=12.5,
        spatial_resolution=10.0,
        processing_level="Level-2A",
        license="EU Copernicus Open Data Policy",
        attribution="© European Union, Copernicus Sentinel-2 data [2026]",
        epistemic_level=EpistemicLevel.OBSERVED,
    )

    assert scene.epistemic_level == EpistemicLevel.OBSERVED
    assert scene.epistemic_level != EpistemicLevel.PREDICTED
    assert scene.epistemic_level != EpistemicLevel.DETECTED
    assert scene.epistemic_level != EpistemicLevel.AI_INTERPRETATION


def test_future_prediction_structural_requirements():
    """
    Proves that a FuturePrediction must have an explicitly modeled scenario, forecast model version,
    and target year in the future (target_year > training_end_year).
    """
    aoi_id = uuid.uuid4()

    # Valid FuturePrediction
    pred = FuturePrediction(
        area_of_interest_id=aoi_id,
        target_year=2035,
        scenario="SSP2-4.5_BUSINESS_AS_USUAL",
        prediction_type=FuturePredictionType.URBAN_EXPANSION,
        prediction_value=142.5,
        unit="km2",
        model_name="CA_Markov_MultiDecadal_Forecaster",
        model_version="1.2.0",
        training_start_year=1990,
        training_end_year=2026,
        confidence=0.87,
        evidence_strength=EvidenceStrength.STRONG,
        assumptions={"annual_growth_rate": 0.035},
        limitations={"sensor_resolution_limit": "10m"},
    )

    assert pred.target_year > pred.training_end_year
    assert pred.target_year == 2035
    assert pred.scenario == "SSP2-4.5_BUSINESS_AS_USUAL"
    assert pred.model_version == "1.2.0"
