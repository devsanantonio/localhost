"""Build data/catalog.json: every public layer from every publisher, and what changed since last time.

    python3 scripts/catalog.py

The ArcGIS publishers come from `peek --all`. VIA's feeds, the USGS gauges and
the aquifer authority's well data aren't ArcGIS layers, so they're listed here
by hand. Each run compares against the last catalog and writes data/changes.json:
every layer its publisher updated in the last 14 days, newest first, with the ones
that weren't in the last catalog marked new.
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

# Sources that aren't ArcGIS layers. "modified" is the date we last confirmed each one by hand,
# not when it changed: they don't report a date, and stamping today's would float them to the top every week.
EXTRA = [
    {"title": "VIA schedule (GTFS): routes, stops, trips", "publisher": "VIA Metropolitan Transit", "type": "GTFS", "modified": "2026-11-02",
     "url": "https://www.viainfo.net/BusService/google_transit.zip", "summary": "Every route, stop and scheduled trip.",
     "credit": "Data provided by VIA Metropolitan Transit"},
    {"title": "VIA realtime: vehicle positions, trip updates, alerts", "publisher": "VIA Metropolitan Transit",
     "type": "GTFS-realtime", "modified": "2026-10-29", "url": "https://www.viainfo.net/developers-resources/",
     "summary": "Live buses, served over http: put a small server in between for a browser app.",
     "credit": "Data provided by VIA Metropolitan Transit"},
    {"title": "USGS live stream gauges, San Antonio", "publisher": "U.S. Geological Survey", "type": "API", "modified": "2026-11-02",
     "url": "https://waterservices.usgs.gov/nwis/iv/?format=json&sites=08178000,08178500&parameterCd=00065,00060",
     "summary": "Water height and flow every 15 minutes. creek-levels reads it.", "credit": "Data: U.S. Geological Survey"},
    {"title": "J-17 index well water level (CSV, since 1992)", "publisher": "Edwards Aquifer Authority", "type": "CSV", "modified": "2026-11-02",
     "url": "https://data.edwardsaquifer.org/GroundWater/DownloadGroundwaterCsv?siteId=J17WL&sensorName=WLE",
     "summary": "Every 15 minutes, newest first. aquifer-today reads it.", "credit": "Data: Edwards Aquifer Authority"},
]


def load(name):
    try:
        with open(os.path.join(DATA, name)) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


if __name__ == "__main__":
    out = subprocess.run([sys.executable, os.path.join(ROOT, "starters", "peek", "main.py"), "--all", "--json"],
                         capture_output=True, text=True, timeout=600, check=True).stdout
    layers = json.loads(out) + EXTRA
    # A catalog that came back nearly empty is an outage, not the publishers deleting everything.
    previous = load("catalog.json")
    if previous and len(layers) < 0.5 * previous["count"]:
        sys.exit(f"Only {len(layers)} layers came back (last time {previous['count']}). Keeping the old catalog.")

    by = {}
    for l in layers:
        by[l["publisher"]] = by.get(l["publisher"], 0) + 1
    catalog = {"generated": datetime.now(timezone.utc).isoformat(timespec="seconds"), "count": len(layers),
               "by_publisher": dict(sorted(by.items(), key=lambda kv: -kv[1])), "layers": layers}

    # What changed: every layer its publisher updated in the last two weeks, by the publisher's own date,
    # marked "new" if it wasn't in the last catalog. Works on the first run too.
    window = (datetime.now(timezone.utc) - timedelta(days=14)).date().isoformat()
    before = {l["url"] for l in previous["layers"]} if previous else None
    changes = [dict(l, change="new" if before is not None and l["url"] not in before else "updated")
               for l in layers if l["modified"] >= window and l["type"] not in ("GTFS", "GTFS-realtime", "API", "CSV")]
    changes.sort(key=lambda l: (l["modified"], l["change"] == "new"), reverse=True)
    since = window
    with open(os.path.join(DATA, "catalog.json"), "w") as f:
        json.dump(catalog, f, indent=1)
        f.write("\n")
    with open(os.path.join(DATA, "changes.json"), "w") as f:
        json.dump({"since": since, "until": catalog["generated"], "changes": changes[:60]}, f, indent=1)
        f.write("\n")
    print(f"{catalog['count']} layers from {len(by)} publishers; {len(changes)} updated since {since}.")
