"""San Antonio's acequias: the Spanish irrigation ditches the city grew around.

Bexar County maps every stretch of acequia dug from the river and San Pedro
Creek after 1718, with the year each was dug and the year it was abandoned.
This script asks which ran near a point (Geekdom's corner, unless you give
another), then writes map.html, a page with a year slider that shows which
ditches were flowing when.

    python3 main.py
    python3 main.py --near 29.4241,-98.4936 --meters 300
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

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--near", help="lat,lon (default: Geekdom, Houston and Soledad)")
    ap.add_argument("--meters", type=int, default=400, help="how far to look (default 400)")
    args = ap.parse_args()
    lat, lon = map(float, args.near.split(",")) if args.near else GEEKDOM

    print(f"Acequias within {args.meters} m of {lat:.5f}, {lon:.5f}:")
    rows = near(lat, lon, args.meters)
    for name, (d, p) in rows:
        print(f"  {d:5.0f} m  {name}, dug {p['YrCreate']}, dry by {p['YrAband']}  ({p['Associated']})")
    if not rows:
        print("  none. Try a bigger --meters, or a point nearer the river.")

    every = {"type": "FeatureCollection", "features": query(where="1=1")}
    with open(os.path.join(HERE, "acequias.geojson"), "w") as f:
        json.dump(every, f)
    with open(os.path.join(HERE, "map.html"), "w") as f:
        f.write(PAGE.replace("__DATA__", json.dumps(every)).replace("__COUNT__", str(len(every["features"]))))
    print(f"Wrote map.html and acequias.geojson: {len(every['features'])} stretches of acequia.")
    print("Data: Bexar County Information Technology GIS")
