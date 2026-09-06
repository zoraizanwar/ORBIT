import pytest
from app.services.forecasting.models import FeatureVector
from app.services.forecasting.forecast_models import LinearTrendModel, MODEL_REGISTRY


def test_linear_trend_model_downward_trend():
    features = [
        FeatureVector(time_coordinate=0.0, year=2020, value=0.70),
        FeatureVector(time_coordinate=1.0, year=2021, value=0.65),
        FeatureVector(time_coordinate=2.0, year=2022, value=0.60),
        FeatureVector(time_coordinate=3.0, year=2023, value=0.55),
    ]

    model = LinearTrendModel()
    model.fit(features)

    assert model.is_fitted is True
    assert model.beta_1 == pytest.approx(-0.05, abs=1e-3)
    assert model.beta_0 == pytest.approx(0.70, abs=1e-3)

    # Predict year 2025 (t=5.0)
    pred_val, lower, upper = model.predict(target_t=5.0, confidence_level=0.95)
    assert pred_val == pytest.approx(0.45, abs=1e-3)
    assert lower is not None and upper is not None
    assert lower <= pred_val <= upper


def test_linear_trend_model_zero_variance():
    # Constant historical series
    features = [
        FeatureVector(time_coordinate=0.0, year=2020, value=0.50),
        FeatureVector(time_coordinate=1.0, year=2021, value=0.50),
        FeatureVector(time_coordinate=2.0, year=2022, value=0.50),
        FeatureVector(time_coordinate=3.0, year=2023, value=0.50),
    ]

    model = LinearTrendModel()
    model.fit(features)

    assert model.beta_1 == pytest.approx(0.0, abs=1e-4)
    assert model.beta_0 == pytest.approx(0.50, abs=1e-4)

    pred_val, lower, upper = model.predict(target_t=4.0)
    assert pred_val == 0.50
    assert lower == 0.50
    assert upper == 0.50


def test_model_registry_security():
    assert "LINEAR_TREND" in MODEL_REGISTRY
    assert "ORBIT-LT-v1" in MODEL_REGISTRY
    assert "ARBITRARY_UNTRUSTED_MODEL" not in MODEL_REGISTRY
