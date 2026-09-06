import pytest
from app.services.geo.query_normalizer import (
    normalize_search_query,
    extract_query_tokens,
    parse_query_and_admin_context,
)


def test_normalize_search_query_cases():
    assert normalize_search_query("Lahore") == "lahore"
    assert normalize_search_query("  LAHORE   ") == "lahore"
    assert normalize_search_query("lahore, pakistan") == "lahore pakistan"
    assert normalize_search_query("M.M. Alam Road") == "m.m. alam road"


def test_extract_query_tokens():
    tokens = extract_query_tokens("Lahore, Punjab, Pakistan")
    assert tokens == ["lahore", "punjab", "pakistan"]

    empty_tokens = extract_query_tokens("   , ;   ")
    assert empty_tokens == []


def test_parse_query_and_admin_context():
    primary, admin = parse_query_and_admin_context("Lahore, Punjab, Pakistan")
    assert primary == "lahore"
    assert admin == ["punjab", "pakistan"]

    single_term, admin2 = parse_query_and_admin_context("Amazonas")
    assert single_term == "amazonas"
    assert admin2 == []
