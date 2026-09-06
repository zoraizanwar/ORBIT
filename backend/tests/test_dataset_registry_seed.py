from app.db.seed import SEED_DATASETS
from app.models.enums import SensingModality


def test_seed_dataset_registry_definitions():
    """Verify that all core public satellite & vector datasets are included in seed definitions."""
    dataset_ids = {ds["id"] for ds in SEED_DATASETS}
    
    assert "copernicus-s2-l2a" in dataset_ids
    assert "copernicus-s1-grd" in dataset_ids
    assert "usgs-landsat-c2l2" in dataset_ids
    assert "copernicus-dem-30" in dataset_ids
    assert "osm-roads-planet" in dataset_ids
    assert "hydrosheds-v1" in dataset_ids
    
    # Check that each dataset has proper licensing metadata and attribution
    for ds in SEED_DATASETS:
        assert ds["provider"] != ""
        assert ds["license"] != ""
        assert ds["attribution"] != ""
        assert isinstance(ds["modality"], SensingModality)
        assert ds["redistribution_allowed"] is True
        assert ds["active"] is True
