import pytest
from app.services.geo.gazetteer_search import (
    calculate_relevance_score,
    get_default_zoom_for_entity_type,
)


def test_calculate_relevance_score_exact():
    score, match_type = calculate_relevance_score(
        query_norm="lahore",
        entity_norm="lahore",
        population=11126285,
    )
    assert match_type == "EXACT"
    assert score >= 0.95


def test_calculate_relevance_score_alias():
    score, match_type = calculate_relevance_score(
        query_norm="lhe",
        entity_norm="lahore",
        alternate_names=["LHE", "لاہور"],
    )
    assert match_type == "ALIAS"
    assert score >= 0.90


def test_calculate_relevance_score_prefix():
    score, match_type = calculate_relevance_score(
        query_norm="laho",
        entity_norm="lahore",
    )
    assert match_type == "PREFIX"
    assert score >= 0.80


def test_calculate_relevance_score_admin_bonus():
    score_with_admin, _ = calculate_relevance_score(
        query_norm="lahore",
        entity_norm="lahore",
        admin_tokens=["punjab", "pakistan"],
        admin_context="Punjab, Pakistan",
    )
    score_without_admin, _ = calculate_relevance_score(
        query_norm="lahore",
        entity_norm="lahore",
    )
    assert score_with_admin > score_without_admin


def test_default_zoom_hierarchy():
    assert get_default_zoom_for_entity_type("COUNTRY") < get_default_zoom_for_entity_type("STATE")
    assert get_default_zoom_for_entity_type("STATE") < get_default_zoom_for_entity_type("CITY")
    assert get_default_zoom_for_entity_type("CITY") < get_default_zoom_for_entity_type("ROAD")
    assert get_default_zoom_for_entity_type("ROAD") < get_default_zoom_for_entity_type("STREET")
