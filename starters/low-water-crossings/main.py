"""Low water crossings near you: the places a road dips through a creek, from Opportunity Home San Antonio.

Opportunity Home San Antonio, the city's housing authority, publishes a map of
the 156 low water crossings inside the FEMA floodplain in Bexar County. This
lists the ones nearest a point (Geekdom's corner, unless you give another) and
writes map.html, a page with every crossing on it.

    python3 main.py
    python3 main.py --near 29.5150,-98.5320 --count 5
    python3 main.py --json
    open map.html

THIS IS NOT A FLOOD WARNING. It shows where crossings are, not whether they are
under water. For road closures and warnings, use BexarFlood.org and the National
Weather Service (weather.gov/ewx). Turn around, don't drown.

Data: Opportunity Home San Antonio
"""
import argparse
import json
import math
import os
import urllib.parse
import urllib.request

SERVICE = (
    "https://services2.arcgis.com/nH68joXCaOE0Iiws/arcgis/rest/services/"
    "Opportunity_Home___Low_Water_Crossings_WFL1/FeatureServer/1/query"
)
HERE = os.path.dirname(os.path.abspath(__file__))
GEEKDOM = (29.42637, -98.49337)   # Houston and Soledad
WARNING = "This is not a flood warning. For closures and warnings: BexarFlood.org and weather.gov/ewx. Turn around, don't drown."
# The layer says its points come from the City of San Antonio's Transportation & Capital Improvements and GIS.
CREDIT = "Data: Opportunity Home San Antonio (points from the City of San Antonio)"


def crossings():
    params = {"where": "1=1", "outFields": "Name,CartID", "outSR": 4326, "f": "geojson"}
    with urllib.request.urlopen(f"{SERVICE}?{urllib.parse.urlencode(params)}", timeout=60) as res:
        return json.load(res)["features"]


def meters(lat, lon, lat2, lon2):
    """Haversine distance in meters."""
    p1, p2 = math.radians(lat), math.radians(lat2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon) / 2) ** 2
    return 6_371_000 * 2 * math.asin(math.sqrt(a))


PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Low water crossings, Bexar County</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>
  html, body, #map { height: 100%; margin: 0; font: 14px system-ui, sans-serif; }
  .panel { position: absolute; z-index: 1000; top: 12px; right: 12px; max-width: 280px; background: #fff;
           padding: 12px 14px; border-radius: 10px; box-shadow: 0 2px 12px rgb(0 0 0 / .15); }
  .panel h1 { font-size: 16px; margin: 0 0 4px; } .panel p { margin: 0 0 6px; color: #525252; }
  .warn { color: #b91c1c !important; font-weight: 600; }
</style></head><body>
<div id="map"></div>
<div class="panel">
  <h1>Low water crossings</h1>
  <p>__COUNT__ crossings inside the FEMA floodplain in Bexar County.</p>
  <p class="warn">Not a flood warning: this shows where they are, not whether they are flooded.
  Check BexarFlood.org. Turn around, don't drown.</p>
</div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
const data = __DATA__;
const map = L.map('map').setView([__LAT__, __LON__], 12);
L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
  maxZoom: 16,
  attribution: 'Data: Opportunity Home San Antonio · Basemap: Esri, HERE, Garmin, &copy; OpenStreetMap contributors'
}).addTo(map);
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
L.geoJSON(data, {
  pointToLayer: (f, ll) => L.circleMarker(ll, {radius: 5, weight: 1, color: '#0a0a0a', fillColor: '#00b2a9', fillOpacity: .9}),
  onEachFeature: (f, l) => l.bindPopup(`<b>${esc(f.properties.Name)}</b>`)
}).addTo(map);
</script></body></html>
"""

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--near", help="lat,lon (default: Geekdom, Houston and Soledad)")
    ap.add_argument("--count", type=int, default=8, help="how many of the nearest to list (default 8)")
    ap.add_argument("--json", action="store_true", help="print JSON instead of a list (and skip map.html)")
    args = ap.parse_args()
    lat, lon = map(float, args.near.split(",")) if args.near else GEEKDOM

    features = [f for f in crossings() if f.get("geometry")]
    nearest = sorted(
        ({"name": " ".join((f["properties"]["Name"] or "").split()), "id": f["properties"]["CartID"],
          "lat": f["geometry"]["coordinates"][1], "lon": f["geometry"]["coordinates"][0],
          "meters": round(meters(lat, lon, f["geometry"]["coordinates"][1], f["geometry"]["coordinates"][0]))}
         for f in features),
        key=lambda c: c["meters"])[: args.count]

    if args.json:
        print(json.dumps({"near": {"lat": lat, "lon": lon}, "total": len(features), "nearest": nearest,
                          "warning": WARNING, "credit": CREDIT}, indent=2))
        raise SystemExit

    print(WARNING + "\n")
    print(f"The {len(nearest)} low water crossings nearest {lat:.5f}, {lon:.5f} (of {len(features)} in Bexar County):\n")
    for c in nearest:
        print(f"  {c['meters'] / 1609.34:5.1f} mi  {c['name']}")
    with open(os.path.join(HERE, "map.html"), "w") as f:
        f.write(PAGE.replace("__DATA__", json.dumps({"type": "FeatureCollection", "features": features}))
                .replace("__COUNT__", str(len(features))).replace("__LAT__", str(lat)).replace("__LON__", str(lon)))
    print(f"\nWrote map.html: all {len(features)} crossings.")
    print(CREDIT)
