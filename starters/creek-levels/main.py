"""San Antonio's creeks right now: live USGS gauges, and the River Authority's draft floodplains.

The U.S. Geological Survey measures the water in San Antonio's river and creeks
every 15 minutes: how high it stands at the gauge, and how much is flowing.
This prints the latest reading at each gauge and how it has moved over the last
day. Give it a point and it also says whether that point falls inside the San
Antonio River Authority's draft floodplain maps.

    python3 main.py
    python3 main.py --site 08178000 --site 08178800
    python3 main.py --near 29.4241,-98.4936
    python3 main.py --json

THIS IS NOT A FLOOD WARNING. Gauges lag, and a creek can rise fast. For
warnings, use the National Weather Service (weather.gov/ewx) and BexarFlood.org.
Turn around, don't drown.

Data: U.S. Geological Survey
This uses River Authority's data but is not endorsed or verified by River Authority.
"""
import argparse
import json
import urllib.parse
import urllib.request
from datetime import date

USGS = "https://waterservices.usgs.gov/nwis/iv/"
# The two gauges downtown. Find more at waterdata.usgs.gov (search "San Antonio, TX").
SITES = ["08178000", "08178500"]   # San Antonio River at San Antonio, San Pedro Creek at Furnish St
HEIGHT, FLOW = "00065", "00060"     # gage height (ft), discharge (cubic feet per second)

# The River Authority's draft floodplain maps, one layer per watershed. They are
# proposals from its 2022/23 studies, not the effective FEMA maps.
FLOODPLAIN = "https://services2.arcgis.com/Eb8y2VjBgkqbQJwk/arcgis/rest/services/Draft_Floodplain/FeatureServer"
WARNING = "This is not a flood warning. For warnings: weather.gov/ewx and BexarFlood.org. Turn around, don't drown."


def get(url, **params):
    with urllib.request.urlopen(url + "?" + urllib.parse.urlencode(params), timeout=60) as res:
        return json.load(res)


def gauges(sites):
    """The last day of readings at each gauge: latest value and the change since a day ago."""
    data = get(USGS, format="json", sites=",".join(sites), parameterCd=f"{HEIGHT},{FLOW}", period="P1D")
    out = {}
    for ts in data["value"]["timeSeries"]:
        site = ts["sourceInfo"]["siteCode"][0]["value"]
        values = [v for v in ts["values"][0]["value"] if v["value"] not in ("", "-999999")]
        if not values:
            continue
        g = out.setdefault(site, {"site": site, "name": ts["sourceInfo"]["siteName"]})
        key = "height_ft" if ts["variable"]["variableCode"][0]["value"] == HEIGHT else "flow_cfs"
        latest, first = float(values[-1]["value"]), float(values[0]["value"])
        g[key] = latest
        g[key + "_change_24h"] = round(latest - first, 2)
        g["as_of"] = values[-1]["dateTime"]
    return list(out.values())


def floodplain(lat, lon):
    """Which draft floodplain zones, if any, the point falls inside."""
    layers = [l["id"] for l in get(FLOODPLAIN, f="json")["layers"]]
    hits = []
    for layer in layers:
        found = get(f"{FLOODPLAIN}/{layer}/query", f="json", geometry=f"{lon},{lat}", geometryType="esriGeometryPoint",
                    inSR=4326, spatialRel="esriSpatialRelIntersects", outFields="FLD_ZONE,ZONE_SUBTY,Watershed",
                    returnGeometry="false")
        for f in found.get("features", []):
            a = f["attributes"]
            hits.append({"watershed": a.get("Watershed"), "zone": a.get("FLD_ZONE"), "description": a.get("ZONE_SUBTY")})
    return hits


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--site", action="append", help="a USGS gauge number (repeat for more; default: the two downtown)")
    ap.add_argument("--near", help="lat,lon to check against the River Authority's draft floodplain maps")
    ap.add_argument("--json", action="store_true", help="print JSON instead of a table")
    args = ap.parse_args()

    result = {"gauges": gauges(args.site or SITES), "warning": WARNING,
              "credit": ["Data: U.S. Geological Survey"]}
    if args.near:
        lat, lon = map(float, args.near.split(","))
        result["point"] = {"lat": lat, "lon": lon, "draft_floodplain": floodplain(lat, lon)}
        result["credit"].append(f"This uses River Authority's data but is not endorsed or verified by River Authority. "
                                f"Retrieved {date.today():%B %-d, %Y}.")

    if args.json:
        print(json.dumps(result, indent=2))
        raise SystemExit

    print(WARNING + "\n")
    for g in result["gauges"]:
        print(g["name"], f"(USGS {g['site']}) · {g['as_of'][:16].replace('T', ' ')}")
        if "height_ft" in g:
            print(f"  water height  {g['height_ft']:>8.2f} ft   {g['height_ft_change_24h']:+.2f} ft in 24 h")
        if "flow_cfs" in g:
            print(f"  flow          {g['flow_cfs']:>8,.1f} cfs  {g['flow_cfs_change_24h']:+,.1f} cfs in 24 h")
    if not result["gauges"]:
        print("No readings came back. Check the gauge numbers at waterdata.usgs.gov.")
    if args.near:
        hits = result["point"]["draft_floodplain"]
        print(f"\n{args.near} in the River Authority's draft floodplain maps (proposed, not the effective FEMA maps):")
        for h in hits:
            print(f"  {h['watershed']}: zone {h['zone']}" + (f", {h['description']}" if h["description"] else ""))
        if not hits:
            print("  outside every draft floodplain zone. That is not a promise it can't flood.")
    print()
    print("\n".join(result["credit"]))
