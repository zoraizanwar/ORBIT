import re
import unicodedata
from typing import List, Tuple


def normalize_search_query(query: str) -> str:
    """
    Normalizes a user search query for deterministic text comparison:
    - Strips leading and trailing whitespace
    - Converts to lowercase
    - Collapses multiple whitespace characters to a single space
    - Normalizes unicode NFKC while preserving geographic characters
    """
    if not query:
        return ""

    # Normalize unicode to compatibility composition form
    normalized = unicodedata.normalize("NFKC", query)
    normalized = normalized.lower().strip()

    # Replace commas, semicolons, and pipes with spaces for token splitting
    normalized = re.sub(r"[,;|]+", " ", normalized)

    # Collapse multiple whitespace
    normalized = re.sub(r"\s+", " ", normalized).strip()

    return normalized


def extract_query_tokens(query: str) -> List[str]:
    """
    Splits normalized query into non-empty tokens.
    """
    norm = normalize_search_query(query)
    if not norm:
        return []
    return [t for t in norm.split(" ") if len(t) > 0]


def parse_query_and_admin_context(raw_query: str) -> Tuple[str, List[str]]:
    """
    Extracts primary query term and potential administrative context tokens.
    Example: 'Lahore, Punjab, Pakistan' -> ('lahore', ['punjab', 'pakistan'])
    """
    if not raw_query:
        return ("", [])

    parts = [p.strip() for p in re.split(r"[,;/]+", raw_query) if p.strip()]
    if not parts:
        return ("", [])

    primary_name = normalize_search_query(parts[0])
    admin_tokens = [normalize_search_query(p) for p in parts[1:] if p.strip()]

    return (primary_name, admin_tokens)
