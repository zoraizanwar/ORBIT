import numpy as np
import pytest
from app.models.enums import EpistemicLevel
from app.services.eo.raster.vegetation_intelligence import (
    analyze_vegetation_canopy,
    VegetationClassificationThresholds,
)
from app.services.eo.raster.water_intelligence import (
    analyze_water_coverage,
    WaterClassificationThresholds,
)
from app.services.eo.raster.urban_intelligence import (
    analyze_built_up_coverage,
    UrbanClassificationThresholds,
)


def test_analyze_vegetation_canopy_stratification():
    # 4 pixels: non-veg (0.1), low (0.3), moderate (0.5), dense (0.7)
    ndvi_arr = np.ma.masked_array(np.array([[0.1, 0.3], [0.5, 0.7]], dtype=np.float32), mask=False)

    summary = analyze_vegetation_canopy(
        ndvi_array=ndvi_arr,
        pixel_res_x=10.0,
        pixel_res_y=10.0,
    )

    assert summary.epistemic_level == EpistemicLevel.CALCULATED
    assert summary.non_vegetated_percentage == 25.0
    assert summary.low_vegetation_percentage == 25.0
    assert summary.moderate_vegetation_percentage == 25.0
    assert summary.dense_vegetation_percentage == 25.0
    assert summary.total_vegetated_percentage == 75.0


def test_analyze_water_coverage():
    # 2 pixels: water (0.4), land (-0.2)
    ndwi_arr = np.ma.masked_array(np.array([[0.4, -0.2]], dtype=np.float32), mask=False)

    water_summary = analyze_water_coverage(
        ndwi_array=ndwi_arr,
        pixel_res_x=10.0,
        pixel_res_y=10.0,
    )

    assert water_summary.epistemic_level == EpistemicLevel.CALCULATED
    assert water_summary.water_candidate_pixel_count == 1
    assert water_summary.water_candidate_percentage == 50.0
    assert water_summary.non_water_percentage == 50.0


def test_analyze_urban_built_up_coverage():
    # 2 pixels: built-up (0.3), non-built (-0.4)
    ndbi_arr = np.ma.masked_array(np.array([[0.3, -0.4]], dtype=np.float32), mask=False)

    urban_summary = analyze_built_up_coverage(
        ndbi_array=ndbi_arr,
        pixel_res_x=10.0,
        pixel_res_y=10.0,
    )

    assert urban_summary.epistemic_level == EpistemicLevel.CALCULATED
    assert urban_summary.built_up_candidate_pixel_count == 1
    assert urban_summary.built_up_candidate_percentage == 50.0
