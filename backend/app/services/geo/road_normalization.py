from typing import Any, Dict, Optional, Tuple


# Canonical ORBIT highway classification mapping from OpenStreetMap tags
HIGHWAY_CLASS_HIERARCHY = {
    # Tier 1: Continental & Primary Corridors
    "motorway": "motorway",
    "motorway_link": "motorway",
    "trunk": "trunk",
    "trunk_link": "trunk",
    "primary": "primary",
    "primary_link": "primary",
    # Tier 2: Regional & Secondary Arteries
    "secondary": "secondary",
    "secondary_link": "secondary",
    "tertiary": "tertiary",
    "tertiary_link": "tertiary",
    # Tier 3: Local & Settlement Infrastructure
    "unclassified": "unclassified",
    "residential": "residential",
    "living_street": "residential",
    "service": "service",
    # Tier 4: Rural, Agricultural & Deep Access Spurs
    "track": "track",
    "path": "path",
    "footway": "path",
    "bridleway": "path",
    "cycleway": "path",
    "pedestrian": "path",
    "road": "unclassified",
}

# Standardized surface classifications
SURFACE_CLASSIFICATIONS = {
    "asphalt": "paved",
    "concrete": "paved",
    "paved": "paved",
    "paving_stones": "paved",
    "sett": "paved",
    "cobblestone": "paved",
    "unpaved": "unpaved",
    "compacted": "unpaved",
    "gravel": "unpaved",
    "fine_gravel": "unpaved",
    "dirt": "ground",
    "earth": "ground",
    "ground": "ground",
    "mud": "ground",
    "sand": "ground",
    "wood": "unpaved",
    "grass": "ground",
}


def normalize_highway_class(raw_highway: Optional[str]) -> Optional[str]:
    """
    Normalize raw OpenStreetMap highway tag value into canonical ORBIT road hierarchy.
    Returns None if tag is absent or not recognized as a vehicular/traversable road feature.
    """
    if not raw_highway:
        return None
    cleaned = raw_highway.strip().lower()
    return HIGHWAY_CLASS_HIERARCHY.get(cleaned, "unclassified")


def normalize_surface(raw_surface: Optional[str], highway_class: Optional[str] = None) -> Optional[str]:
    """
    Normalize raw OSM surface tag into standardized surface category:
    paved, unpaved, or ground. Defaults to typical class behavior if unspecified.
    """
    if not raw_surface:
        if highway_class in ["motorway", "trunk", "primary", "secondary"]:
            return "paved"
        elif highway_class == "track":
            return "ground"
        return None
    cleaned = raw_surface.strip().lower()
    return SURFACE_CLASSIFICATIONS.get(cleaned, cleaned)


def parse_lane_count(raw_lanes: Optional[Any], default_lanes: int = 1) -> int:
    """
    Parse lanes tag safely from string/int values, handling split lane values (e.g. '2;3' or '2|1').
    """
    if raw_lanes is None:
        return default_lanes
    if isinstance(raw_lanes, int):
        return max(1, min(raw_lanes, 16))
    if isinstance(raw_lanes, str):
        cleaned = raw_lanes.strip().split(";")[0].split("|")[0]
        try:
            val = int(cleaned)
            return max(1, min(val, 16))
        except ValueError:
            return default_lanes
    return default_lanes


def parse_speed_limit(raw_maxspeed: Optional[Any]) -> Optional[int]:
    """
    Parse maxspeed tag in km/h. Handles numeric strings and unit conversions (e.g. '60 mph').
    """
    if raw_maxspeed is None:
        return None
    if isinstance(raw_maxspeed, (int, float)):
        return int(raw_maxspeed)
    if isinstance(raw_maxspeed, str):
        cleaned = raw_maxspeed.strip().lower()
        if "mph" in cleaned:
            numeric_part = cleaned.replace("mph", "").strip()
            try:
                mph = float(numeric_part)
                return int(round(mph * 1.60934))
            except ValueError:
                return None
        elif "knots" in cleaned:
            return None
        else:
            digits = "".join([c for c in cleaned if c.isdigit()])
            if digits:
                return int(digits)
    return None


def parse_boolean_tag(raw_val: Optional[Any]) -> bool:
    """
    Parse OSM boolean flags (e.g. oneway, bridge, tunnel).
    """
    if raw_val is None:
        return False
    if isinstance(raw_val, bool):
        return raw_val
    if isinstance(raw_val, (int, float)):
        return bool(raw_val)
    if isinstance(raw_val, str):
        cleaned = raw_val.strip().lower()
        return cleaned in ["yes", "true", "1", "-1", "reversible"]
    return False


def normalize_osm_road_properties(osm_tags: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform raw OSM tags dictionary into normalized ORBIT RoadFeature property model.
    """
    raw_highway = osm_tags.get("highway")
    highway_class = normalize_highway_class(raw_highway)
    if not highway_class:
        highway_class = "unclassified"

    surface = normalize_surface(osm_tags.get("surface"), highway_class)
    lanes = parse_lane_count(osm_tags.get("lanes"), default_lanes=1)
    maxspeed = parse_speed_limit(osm_tags.get("maxspeed"))
    oneway = parse_boolean_tag(osm_tags.get("oneway"))
    bridge = parse_boolean_tag(osm_tags.get("bridge"))
    tunnel = parse_boolean_tag(osm_tags.get("tunnel"))
    access = osm_tags.get("access")
    if access:
        access = str(access).strip().lower()

    name = osm_tags.get("name")
    if name:
        name = str(name).strip()[:255]

    ref = osm_tags.get("ref")
    if ref:
        ref = str(ref).strip()[:50]

    return {
        "highway_class": highway_class,
        "name": name,
        "ref": ref,
        "surface": surface,
        "lanes": lanes,
        "maxspeed": maxspeed,
        "oneway": oneway,
        "bridge": bridge,
        "tunnel": tunnel,
        "access": access,
        "source": "OpenStreetMap",
        "source_version": osm_tags.get("source:date") or osm_tags.get("version"),
    }
