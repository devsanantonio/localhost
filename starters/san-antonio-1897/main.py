"""San Antonio in 1896–97, on one map.

Bexar County GIS digitized about 4,200 places from the 1896 Sanborn fire insurance
maps and the 1897 city directory: hospitals, saloons, schools, wagon yards,
churches, breweries. This script fetches them and writes map.html, a single
page you can open in any browser or put on GitHub Pages.

    python3 main.py
    open map.html

Data: Bexar County Information Technology GIS
"""
import json
import os
import urllib.parse
import urllib.request

SERVICE = (
    "https://services1.arcgis.com/8onVmslF2KXErTHT/arcgis/rest/services/"
    "Historic_POI/FeatureServer/0/query"
)
HERE = os.path.dirname(os.path.abspath(__file__))


def fetch_all():
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
        with urllib.request.urlopen(f"{SERVICE}?{params}", timeout=60) as res:
            page = json.load(res)
        features += page["features"]
        if not page.get("properties", {}).get("exceededTransferLimit"):
            return features
        offset += 1000


def clean(features):
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


PAGE = """<!doctype html>
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
    print("Fetching historic places from Bexar County GIS…")
    collection = clean(fetch_all())
    with open(os.path.join(HERE, "places-1897.geojson"), "w") as f:
        json.dump(collection, f)
    with open(os.path.join(HERE, "map.html"), "w") as f:
        f.write(PAGE.replace("__DATA__", json.dumps(collection)))
    print(f"Wrote map.html and places-1897.geojson: {len(collection['features']):,} places.")
    print("Data: Bexar County Information Technology GIS")
