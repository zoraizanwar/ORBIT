import re
from typing import Optional
from pydantic import BaseModel, Field


class ParsedCoordinate(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    formatted_coordinate: str
    camera_zoom: float = 13.0


DECIMAL_PAIR_RE = re.compile(
    r"^([-+]?\d+(?:\.\d+)?)[,\s]+([-+]?\d+(?:\.\d+)?)$"
)
CARDINAL_PAIR_RE = re.compile(
    r"^(\d+(?:\.\d+)?)\s*([NSns])[,\s]+(\d+(?:\.\d+)?)\s*([EWew])$"
)
LABELED_PAIR_RE = re.compile(
    r"(?:lat|latitude)\s*[:=]?\s*([-+]?\d+(?:\.\d+)?)[,\s]+(?:lon|lng|longitude)\s*[:=]?\s*([-+]?\d+(?:\.\d+)?)"
)


def parse_coordinate_query(query: str) -> Optional[ParsedCoordinate]:
    """
    Attempts to parse a user search query as geographic coordinates.
    Returns ParsedCoordinate if valid, or None if the query is not a coordinate pair.
    """
    if not query:
        return None

    cleaned = query.strip()

    # 1. Check labeled lat/lon (e.g. "lat: 31.5204, lon: 74.3587", "latitude: -11.52, longitude: -54.75")
    match = LABELED_PAIR_RE.search(cleaned.lower())
    if match:
        try:
            lat = float(match.group(1))
            lon = float(match.group(2))
            if -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0:
                lat_card = "N" if lat >= 0 else "S"
                lon_card = "E" if lon >= 0 else "W"
                formatted = f"{abs(lat):.4f}° {lat_card}, {abs(lon):.4f}° {lon_card}"
                return ParsedCoordinate(
                    latitude=lat,
                    longitude=lon,
                    formatted_coordinate=formatted,
                    camera_zoom=13.0,
                )
        except (ValueError, TypeError):
            pass

    # 2. Check cardinal format (e.g. "31.5204 N, 74.3587 E" or "12.1 S, 54.78 W")
    match = CARDINAL_PAIR_RE.match(cleaned)
    if match:
        try:
            lat_val = float(match.group(1))
            lat_dir = match.group(2).upper()
            lon_val = float(match.group(3))
            lon_dir = match.group(4).upper()

            lat = lat_val if lat_dir == "N" else -lat_val
            lon = lon_val if lon_dir == "E" else -lon_val

            if -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0:
                formatted = f"{abs(lat):.4f}° {lat_dir}, {abs(lon):.4f}° {lon_dir}"
                return ParsedCoordinate(
                    latitude=lat,
                    longitude=lon,
                    formatted_coordinate=formatted,
                    camera_zoom=13.0,
                )
        except (ValueError, TypeError):
            pass

    # 3. Check simple decimal degrees (e.g. "31.5204, 74.3587" or "-12.1 54.78")
    match = DECIMAL_PAIR_RE.match(cleaned)
    if match:
        try:
            lat = float(match.group(1))
            lon = float(match.group(2))
            if -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0:
                lat_card = "N" if lat >= 0 else "S"
                lon_card = "E" if lon >= 0 else "W"
                formatted = f"{abs(lat):.4f}° {lat_card}, {abs(lon):.4f}° {lon_card}"
                return ParsedCoordinate(
                    latitude=lat,
                    longitude=lon,
                    formatted_coordinate=formatted,
                    camera_zoom=13.0,
                )
        except (ValueError, TypeError):
            pass

    return None
