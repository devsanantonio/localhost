"""San Antonio's history, mapped: the acequias from 1718, and the city of 1896-97.

Bexar County maps every stretch of acequia dug from the river and San Pedro
Creek after 1718, with the year each was dug and the year it was abandoned.
By default this asks which ran near a point (Geekdom's corner, unless you give
another), then writes map.html, a page with a year slider that shows which
ditches were flowing when.

With --1897 it maps the city instead, as the County digitized it from the 1896
Sanborn fire insurance maps and the 1897 city directory: about 4,200 places,
from saloons to schools, written to map-1897.html.

    python3 main.py
    python3 main.py --near 29.4241,-98.4936 --meters 300
    python3 main.py --1897
    python3 main.py --json
    open map.html

Data: Bexar County Information Technology GIS
"""
import argparse
import json
import math
import os
import urllib.parse
import urllib.request

SERVICE = (
    "https://services1.arcgis.com/8onVmslF2KXErTHT/arcgis/rest/services/"
    "RullmanAcequia/FeatureServer/0/query"
)
HERE = os.path.dirname(os.path.abspath(__file__))
GEEKDOM = (29.42637, -98.49337)   # Houston and Soledad


def query(**params):
    params = {"outFields": "Name,Associated,YrCreate,YrAband", "outSR": 4326, "f": "geojson", **params}
    with urllib.request.urlopen(f"{SERVICE}?{urllib.parse.urlencode(params)}", timeout=60) as res:
        return json.load(res)["features"]


def near(lat, lon, meters):
    """Ask the service to do the distance filter, then measure how close each ditch came."""
    found = query(geometry=f"{lon},{lat}", geometryType="esriGeometryPoint", inSR=4326,
                  distance=meters, units="esriSRUnit_Meter", where="1=1")
    kx = 111_320 * math.cos(math.radians(lat))
    closest = {}
    for f in found:
        p = f["properties"]
        name = " ".join(p["Name"].split())
        lines = f["geometry"]["coordinates"]
        if f["geometry"]["type"] == "LineString":
            lines = [lines]
        d = min(segment_distance(lon, lat, a, b, kx) for line in lines for a, b in zip(line, line[1:]))
        if name not in closest or d < closest[name][0]:
            closest[name] = (d, p)
    return sorted(closest.items(), key=lambda kv: kv[1][0])


def segment_distance(lon, lat, a, b, kx):
    """Meters from a point to a line segment, flat-earth: fine across a few blocks."""
    ax, ay = (a[0] - lon) * kx, (a[1] - lat) * 111_320
    bx, by = (b[0] - lon) * kx, (b[1] - lat) * 111_320
    dx, dy = bx - ax, by - ay
    t = max(0.0, min(1.0, -(ax * dx + ay * dy) / ((dx * dx + dy * dy) or 1)))
    return math.hypot(ax + t * dx, ay + t * dy)


PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>San Antonio's acequias</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>
  html, body, #map { height: 100%; margin: 0; font: 14px system-ui, sans-serif; }
  .panel { position: absolute; z-index: 1000; top: 12px; right: 12px; width: 260px; background: #fff;
           padding: 12px 14px; border-radius: 10px; box-shadow: 0 2px 12px rgb(0 0 0 / .15); }
  .panel h1 { font-size: 16px; margin: 0 0 4px; } .panel p { margin: 0 0 8px; color: #525252; }
  #year { font: 600 28px ui-monospace, monospace; } input { width: 100%; }
</style></head><body>
<div id="map"></div>
<div class="panel">
  <h1>San Antonio's acequias</h1>
  <p>Ditches flowing in <span id="year"></span></p>
  <input id="slider" type="range" min="1718" max="2020" value="1800">
  <p><span id="n"></span> of __COUNT__ stretches. Gray ones had gone dry.</p>
</div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
const data = __DATA__;
const map = L.map('map').setView([29.40, -98.48], 12);
L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
  maxZoom: 16,
  attribution: 'Data: Bexar County Information Technology GIS · Basemap: Esri, HERE, Garmin, &copy; OpenStreetMap contributors'
}).addTo(map);
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const layer = L.geoJSON(data, {
  onEachFeature: (f, l) => {
    const p = f.properties;
    l.bindPopup(`<b>${esc(p.Name)}</b><br>${esc(p.Associated)}<br>Dug ${p.YrCreate}, abandoned ${p.YrAband}`);
  }
}).addTo(map);
const slider = document.getElementById('slider');
function draw() {
  const y = +slider.value;
  let n = 0;
  layer.eachLayer(l => {
    const p = l.feature.properties;
    const flowing = p.YrCreate <= y && y < p.YrAband;
    if (flowing) n++;
    l.setStyle(p.YrCreate > y ? {opacity: 0} : {color: flowing ? '#00b2a9' : '#a3a3a3', weight: flowing ? 4 : 2, opacity: 1});
  });
  document.getElementById('year').textContent = y;
  document.getElementById('n').textContent = n;
}
slider.oninput = draw; draw();
</script></body></html>
"""

# ---- 1896-97: the County's historic places, from the Sanborn maps and the 1897 directory ----

POI_1897 = (
    "https://services1.arcgis.com/8onVmslF2KXErTHT/arcgis/rest/services/"
    "Historic_POI/FeatureServer/0/query"
)


def places_1897():
    """The service returns at most 1,000 features a request, so page through."""
    features, offset = [], 0
    while True:
        params = urllib.parse.urlencode({
            "where": "1=1",
            "outFields": "POI,CAT,BUSINESS,NOTES",
            "outSR": 4326,
            "resultOffset": offset,
            "resultRecordCount": 1000,
            "f": "geojson",
        })
        with urllib.request.urlopen(f"{POI_1897}?{params}", timeout=60) as res:
            page = json.load(res)
        features += page["features"]
        if not page.get("properties", {}).get("exceededTransferLimit"):
            return features
        offset += 1000


def clean_1897(features):
    keep = []
    for f in features:
        p = f["properties"]
        if not f.get("geometry") or not (p.get("POI") or "").strip():
            continue
        keep.append({
            "type": "Feature",
            "geometry": f["geometry"],
            "properties": {k: (p.get(k) or "").strip() for k in ("POI", "CAT", "BUSINESS", "NOTES")},
        })
    return {"type": "FeatureCollection", "features": keep}


PAGE_1897 = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>San Antonio, 1896–97</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>
  html, body, #map { height: 100%; margin: 0; font: 14px system-ui, sans-serif; }
  .panel { position: absolute; z-index: 1000; top: 12px; right: 12px; max-width: 260px; background: #fff;
           padding: 12px 14px; border-radius: 10px; box-shadow: 0 2px 12px rgb(0 0 0 / .15); }
  .panel h1 { font-size: 16px; margin: 0 0 4px; } .panel p { margin: 0 0 8px; color: #525252; }
  select { width: 100%; padding: 4px; }
</style></head><body>
<div id="map"></div>
<div class="panel">
  <h1>San Antonio, 1896–97</h1>
  <p><span id="n"></span> places from the Sanborn maps and the 1897 city directory.</p>
  <select id="cat"><option value="">Every kind of place</option></select>
</div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
const data = __DATA__;
const map = L.map('map').setView([29.4241, -98.4936], 15);
L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
  maxZoom: 16,
  attribution: 'Data: Bexar County Information Technology GIS · Basemap: Esri, HERE, Garmin, &copy; OpenStreetMap contributors'
}).addTo(map);
const cats = [...new Set(data.features.map(f => f.properties.CAT))].filter(Boolean).sort();
const sel = document.getElementById('cat');
cats.forEach(c => sel.add(new Option(c[0] + c.slice(1).toLowerCase(), c)));
const esc = s => s.replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
let layer;
function draw() {
  if (layer) layer.remove();
  const shown = data.features.filter(f => !sel.value || f.properties.CAT === sel.value);
  layer = L.geoJSON({type: 'FeatureCollection', features: shown}, {
    pointToLayer: (f, ll) => L.circleMarker(ll, {radius: 3, weight: .5, color: '#0a0a0a', fillColor: '#ff8200', fillOpacity: .8}),
    onEachFeature: (f, l) => {
      const p = f.properties;
      l.bindPopup(`<b>${esc(p.POI)}</b><br>${esc([p.CAT, p.BUSINESS].filter(Boolean).join(' · '))}` +
                  (p.NOTES ? `<br><i>${esc(p.NOTES)}</i>` : ''));
    }
  }).addTo(map);
  document.getElementById('n').textContent = shown.length.toLocaleString();
}
sel.onchange = draw; draw();
</script></body></html>
"""

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--near", help="lat,lon (default: Geekdom, Houston and Soledad)")
    ap.add_argument("--meters", type=int, default=400, help="how far to look (default 400)")
    ap.add_argument("--1897", dest="y1897", action="store_true", help="map the city of 1896-97 instead (writes map-1897.html)")
    ap.add_argument("--json", action="store_true", help="print JSON instead of text (the map is still written)")
    args = ap.parse_args()

    if args.y1897:
        if not args.json:
            print("Fetching historic places from Bexar County GIS…")
        collection = clean_1897(places_1897())
        with open(os.path.join(HERE, "places-1897.geojson"), "w") as f:
            json.dump(collection, f)
        with open(os.path.join(HERE, "map-1897.html"), "w") as f:
            f.write(PAGE_1897.replace("__DATA__", json.dumps(collection)))
        if args.json:
            counts = {}
            for f in collection["features"]:
                cat = f["properties"]["CAT"] or "uncategorized"
                counts[cat] = counts.get(cat, 0) + 1
            print(json.dumps({"places": len(collection["features"]),
                              "by_category": dict(sorted(counts.items(), key=lambda kv: -kv[1])),
                              "files": ["map-1897.html", "places-1897.geojson"],
                              "credit": "Data: Bexar County Information Technology GIS"}, indent=2))
            raise SystemExit
        print(f"Wrote map-1897.html and places-1897.geojson: {len(collection['features']):,} places.")
        print("Data: Bexar County Information Technology GIS")
        raise SystemExit
    lat, lon = map(float, args.near.split(",")) if args.near else GEEKDOM

    rows = near(lat, lon, args.meters)
    every = {"type": "FeatureCollection", "features": query(where="1=1")}
    with open(os.path.join(HERE, "acequias.geojson"), "w") as f:
        json.dump(every, f)
    with open(os.path.join(HERE, "map.html"), "w") as f:
        f.write(PAGE.replace("__DATA__", json.dumps(every)).replace("__COUNT__", str(len(every["features"]))))
    if args.json:
        print(json.dumps({
            "near": {"lat": lat, "lon": lon, "meters": args.meters},
            "acequias": [{"name": name, "meters": round(d), "dug": p["YrCreate"], "dry_by": p["YrAband"],
                          "associated": p["Associated"]} for name, (d, p) in rows],
            "stretches": len(every["features"]), "files": ["map.html", "acequias.geojson"],
            "credit": "Data: Bexar County Information Technology GIS"}, indent=2))
        raise SystemExit

    print(f"Acequias within {args.meters} m of {lat:.5f}, {lon:.5f}:")
    for name, (d, p) in rows:
        print(f"  {d:5.0f} m  {name}, dug {p['YrCreate']}, dry by {p['YrAband']}  ({p['Associated']})")
    if not rows:
        print("  none. Try a bigger --meters, or a point nearer the river.")

    print(f"Wrote map.html and acequias.geojson: {len(every['features'])} stretches of acequia.")
    print("Data: Bexar County Information Technology GIS")
