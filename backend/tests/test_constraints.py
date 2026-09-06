from sqlalchemy import CheckConstraint
from app.models.analysis.analysis_run import AnalysisRun
from app.models.intelligence.detected_change import DetectedChange
from app.models.history_deep.future_prediction import FuturePrediction
from app.models.history_deep.geological_epoch import GeologicalEpoch
from app.models.history_deep.islamic_geographic_record import IslamicGeographicRecord
from app.models.eo.imagery_scene import ImageryScene


def test_analysis_run_constraints_registered():
    """Verify that analysis.runs table defines the date order check constraint."""
    table = AnalysisRun.__table__
    constraint_names = [c.name for c in table.constraints if isinstance(c, CheckConstraint)]
    assert "check_analysis_run_dates" in constraint_names


def test_detected_change_constraints_registered():
    """Verify that detected_changes table defines confidence range and date order constraints."""
    table = DetectedChange.__table__
    constraint_names = [c.name for c in table.constraints if isinstance(c, CheckConstraint)]
    assert "check_change_confidence_range" in constraint_names
    assert "check_change_dates_logical" in constraint_names


def test_future_prediction_constraints_registered():
    """Verify that future_predictions table enforces target_year > training_end_year."""
    table = FuturePrediction.__table__
    constraint_names = [c.name for c in table.constraints if isinstance(c, CheckConstraint)]
    assert "check_prediction_target_after_training" in constraint_names
    assert "check_prediction_training_years" in constraint_names
    assert "check_prediction_confidence_range" in constraint_names
    assert "check_prediction_bounds_logical" in constraint_names


def test_geological_epoch_constraints_registered():
    """Verify that geological_epochs table enforces start_age >= end_age (Ma chronological order)."""
    table = GeologicalEpoch.__table__
    constraint_names = [c.name for c in table.constraints if isinstance(c, CheckConstraint)]
    assert "check_geological_age_order" in constraint_names


def test_islamic_record_constraints_registered():
    """Verify that islamic_geographic_records table enforces confidence bound constraints."""
    table = IslamicGeographicRecord.__table__
    constraint_names = [c.name for c in table.constraints if isinstance(c, CheckConstraint)]
    assert "check_islamic_record_confidence_range" in constraint_names


def test_imagery_scene_cloud_cover_constraint_registered():
    """Verify that imagery_scenes table enforces cloud_cover between 0 and 100%."""
    table = ImageryScene.__table__
    constraint_names = [c.name for c in table.constraints if isinstance(c, CheckConstraint)]
    assert "check_scene_cloud_cover_range" in constraint_names
