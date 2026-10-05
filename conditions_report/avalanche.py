"""
Avalanche danger for Colorado zones, via the avalanche.org Public API.

CAIC (Colorado's own avalanche center) doesn't publish its own API, but the
National Avalanche Center runs an official public API that includes CAIC's
zones and is explicitly meant for 3rd-party use:
https://github.com/NationalAvalancheCenter/Avalanche.org-Public-API-Docs

It returns GeoJSON: one "feature" per forecast zone, each with a polygon
shape and properties like the current danger rating. It does NOT give you
a simple "what zone is lat/lon X in" lookup, so we do that ourselves with
a point-in-polygon check against each zone's shape.

Why we compute the zone instead of hardcoding one in config: CAIC zone
boundaries don't line up neatly with place names -- Loveland Pass, for
example, sits right on the line between two zones. Checking the actual
coordinates against the actual shape is correct; guessing from the name
isn't.
"""

import requests

MAP_LAYER_URL = "https://api.avalanche.org/v2/public/products/map-layer/CAIC"


def _point_in_ring(lon, lat, ring):
    """
    Ray casting algorithm: decides whether (lon, lat) is inside a polygon
    ring (a closed loop of [lon, lat] points) by counting how many times a
    horizontal ray from the point crosses the ring's edges. An odd number
    of crossings means the point is inside.

    This is a classic, dependency-free way to do point-in-polygon. Mapping
    libraries like `shapely` do the same thing under the hood for simple
    cases like this.
    """
    inside = False
    n = len(ring)
    j = n - 1
    for i in range(n):
        xi, yi = ring[i]
        xj, yj = ring[j]
        crosses = (yi > lat) != (yj > lat)
        if crosses:
            x_at_lat = (xj - xi) * (lat - yi) / (yj - yi) + xi
            if lon < x_at_lat:
                inside = not inside
        j = i
    return inside


def _point_in_geometry(lon, lat, geometry):
    """Check a point against a GeoJSON Polygon or MultiPolygon geometry.
    Only checks each polygon's outer boundary (ignores holes), which is
    fine here -- avalanche zones aren't shaped with holes in them."""
    if geometry["type"] == "Polygon":
        polygons = [geometry["coordinates"]]
    elif geometry["type"] == "MultiPolygon":
        polygons = geometry["coordinates"]
    else:
        return False

    for polygon in polygons:
        exterior_ring = polygon[0]
        if _point_in_ring(lon, lat, exterior_ring):
            return True
    return False


def get_avalanche_danger(lat, lon):
    """
    Return the CAIC zone danger info for a location, or None if it's
    unavailable (API down, or the point doesn't fall in any CAIC zone --
    e.g. it's outside Colorado).

    Returns a dict like:
        {
            "zone_name": "Vail & Summit County",
            "danger": "considerable",
            "danger_level": 3,          # -1 means "no rating" (off-season)
            "color": "#f7931e",         # CAIC's own color for this rating
            "travel_advice": "...",
            "link": "https://avalanche.state.co.us/...",
        }
    """
    try:
        resp = requests.get(MAP_LAYER_URL, timeout=10)
        resp.raise_for_status()
        zones = resp.json()["features"]
    except requests.RequestException as e:
        print(f"  [avalanche] could not fetch CAIC zones: {e}")
        return None
    except KeyError as e:
        print(f"  [avalanche] unexpected response shape: {e}")
        return None

    for zone in zones:
        if _point_in_geometry(lon, lat, zone["geometry"]):
            p = zone["properties"]
            return {
                "zone_name": p["name"],
                "danger": p["danger"],
                "danger_level": p["danger_level"],
                "color": p["color"],
                "travel_advice": p["travel_advice"],
                "link": p["link"],
            }

    print(f"  [avalanche] no CAIC zone found for ({lat}, {lon})")
    return None


if __name__ == "__main__":
    # Quick manual test: python conditions_report/avalanche.py
    print(get_avalanche_danger(39.4817, -106.1319))   # Copper Mountain
    print(get_avalanche_danger(39.6636, -105.8792))   # Loveland Pass
    print(get_avalanche_danger(39.5306, -106.2172))   # Vail Pass
