"""The busiest roads, and what's being built on them: the Texas Department of Transportation's open data.

TxDOT counts traffic at fixed stations on state roads across Texas and publishes the
Annual Average Daily Traffic (AADT) at each: how many vehicles pass on an average day,
with up to twenty years of history per station. It also publishes every construction
project it runs, with its stage, limits and estimated cost. This asks both for one
county (Bexar by default), and lets the server do the filtering and the adding up.

    python3 main.py                        # the busiest count stations in Bexar County, 2025
    python3 main.py --grew                 # the stations whose traffic grew most since 2019
    python3 main.py --near 29.4241,-98.4936             # stations within 1,600 m of a point, and their trend
    python3 main.py --building             # TxDOT's active projects: by stage, then the biggest
    python3 main.py --county Travis        # any Texas county
    python3 main.py --json

Data: Texas Department of Transportation
"""
import argparse
import json
import re
import urllib.parse
import urllib.request

BASE = "https://services.arcgis.com/KTcxiTD9dsQw4r7Z/ArcGIS/rest/services"
AADT = f"{BASE}/TxDOT_AADT_Annuals_(Public_View)/FeatureServer/0/query"
PROJECTS = f"{BASE}/TxDOT_DCIS_All_Projects/FeatureServer/0/query"
CREDIT = "Data: Texas Department of Transportation"
HISTORY = 19            # AADT_RPT_HIST_01_QTY (last year) .. _19_QTY (19 years back)
BASELINE_YEARS_BACK = 6  # 2019 when the latest year is 2025: before the pandemic dip

# TxDOT writes roads as a two-letter system and a zero-padded number: IH0410, LP1604, FM2252.
SYSTEMS = {"IH": "I-", "US": "US ", "SH": "SH ", "FM": "FM ", "RM": "RM ", "LP": "Loop ", "SL": "Loop ",
           "SS": "Spur ", "BI": "Business I-", "BU": "Business US ", "BS": "Business SH ", "BF": "Business FM ",
           "PR": "Park Road ", "PA": "Principal Arterial ", "CR": "County Road "}


def road(code):
    code = (code or "").strip().upper()
    m = re.match(r"^([A-Z]{2})\s*0*(\d+)\s*([A-Z]?)$", code)
    if m:
        return f"{SYSTEMS.get(m.group(1), m.group(1) + ' ')}{m.group(2)}{m.group(3)}"
    return code if re.search(r"[A-Z0-9]", code) else "road not listed"


def query(url, **params):
    params = {"where": "1=1", "returnGeometry": "false", "f": "json", **params}
    with urllib.request.urlopen(url + "?" + urllib.parse.urlencode(params), timeout=60) as res:
        data = json.load(res)
    if "error" in data:
        raise SystemExit(f"The service said: {data['error'].get('message', data['error'])}")
    return data


def rows(url, **params):
    """Every matching row, paged: the services return at most 2,000 to 5,000 at a time."""
    out, offset = [], 0
    while True:
        data = query(url, resultOffset=offset, **params)
        out += [f["attributes"] for f in data["features"]]
        if not data.get("exceededTransferLimit"):
            return out
        offset = len(out)


def county_where(field, county):
    return f"UPPER({field}) = '{county.replace(chr(39), '').upper()}'"


def station(r):
    year = r["AADT_RPT_YEAR"]
    history = {year: r["AADT_RPT_QTY"]}
    for k in range(1, HISTORY + 1):
        if r.get(f"AADT_RPT_HIST_{k:02d}_QTY") is not None:
            history[year - k] = r[f"AADT_RPT_HIST_{k:02d}_QTY"]
    return {"station": r["TRFC_STATN_ID"], "road": road(r["ON_ROAD"]), "year": year, "vehicles_per_day": r["AADT_RPT_QTY"],
            "lat": r["LATITUDE"], "lon": r["LONGITUDE"], "history": dict(sorted(history.items()))}


FIELDS = "TRFC_STATN_ID,ON_ROAD,AADT_RPT_YEAR,AADT_RPT_QTY,LATITUDE,LONGITUDE," + ",".join(
    f"AADT_RPT_HIST_{k:02d}_QTY" for k in range(1, HISTORY + 1))


def busiest(county, limit=15):
    data = query(AADT, where=f"{county_where('CNTY_NM', county)} AND AADT_RPT_QTY IS NOT NULL",
                 orderByFields="AADT_RPT_QTY DESC", resultRecordCount=limit, outFields=FIELDS)
    return [station(f["attributes"]) for f in data["features"]]


def grew(county, limit=15, floor=10000):
    """Stations with the largest change since the baseline year, among those carrying at least `floor` a day."""
    out = []
    for r in rows(AADT, where=county_where("CNTY_NM", county), outFields=FIELDS):
        s = station(r)
        base_year = s["year"] - BASELINE_YEARS_BACK
        base = s["history"].get(base_year)
        if base and base >= floor and s["vehicles_per_day"]:
            s["since"] = base_year
            s["change"] = s["vehicles_per_day"] - base
            s["change_pct"] = round(100 * s["change"] / base, 1)
            out.append(s)
    return sorted(out, key=lambda s: -s["change"])[:limit]


def near(lat, lon, meters):
    data = query(AADT, geometry=f"{lon},{lat}", geometryType="esriGeometryPoint", inSR=4326,
                 spatialRel="esriSpatialRelIntersects", distance=meters, units="esriSRUnit_Meter", outFields=FIELDS)
    found = [station(f["attributes"]) for f in data["features"] if f["attributes"]["AADT_RPT_QTY"] is not None]
    return sorted(found, key=lambda s: -s["vehicles_per_day"])


def building(county, limit=10):
    """TxDOT's active projects in the county: totals by stage, then the most expensive."""
    where = f"{county_where('COUNTY_NAME', county)} AND PROJ_STAT = 'Active'"
    stats = [{"statisticType": "count", "onStatisticField": "OBJECTID", "outStatisticFieldName": "projects"},
             {"statisticType": "sum", "onStatisticField": "EST_CONSTRUCTION_COST", "outStatisticFieldName": "cost"}]
    by_stage = [f["attributes"] for f in query(PROJECTS, where=where, groupByFieldsForStatistics="PROJ_STG",
                                               outStatistics=json.dumps(stats))["features"]]
    biggest = query(PROJECTS, where=f"{where} AND EST_CONSTRUCTION_COST IS NOT NULL", orderByFields="EST_CONSTRUCTION_COST DESC",
                    resultRecordCount=limit, outFields="HIGHWAY_NUMBER,LIMITS_FROM,LIMITS_TO,TYPE_OF_WORK,PROJ_CLASS,PROJ_STG,EST_CONSTRUCTION_COST,CONTROL_SECT_JOB")
    return {
        "by_stage": sorted(({"stage": r["PROJ_STG"], "projects": r["projects"], "cost": r["cost"]} for r in by_stage),
                           key=lambda r: -(r["cost"] or 0)),
        "biggest": [{"highway": road(r["HIGHWAY_NUMBER"]), "from": (r["LIMITS_FROM"] or "").strip(), "to": (r["LIMITS_TO"] or "").strip(" ."),
                     "work": (r["TYPE_OF_WORK"] or "").strip().capitalize(), "class": r["PROJ_CLASS"], "stage": r["PROJ_STG"],
                     "cost": r["EST_CONSTRUCTION_COST"], "csj": r["CONTROL_SECT_JOB"]}
                    for r in (f["attributes"] for f in biggest["features"])],
    }


def money(n):
    return f"${n / 1e9:,.2f}B" if n and n >= 1e9 else f"${(n or 0) / 1e6:,.1f}M"


def trend(s, years=(2015, 2019, 2022)):
    return "  ".join(f"{y}: {s['history'][y]:,}" for y in years if y in s["history"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--county", default="Bexar", help="any Texas county (default Bexar)")
    ap.add_argument("--grew", action="store_true", help="stations whose traffic grew most since 2019")
    ap.add_argument("--near", metavar="LAT,LON", help="count stations near a point")
    ap.add_argument("--meters", type=int, default=1600, help="radius for --near (default 1600)")
    ap.add_argument("--building", action="store_true", help="TxDOT's active construction projects")
    ap.add_argument("--json", action="store_true", help="print JSON instead of tables")
    args = ap.parse_args()

    if args.near:
        try:
            lat, lon = (float(x) for x in args.near.split(","))
        except ValueError:
            raise SystemExit("--near takes LAT,LON, for example 29.4241,-98.4936")
        result = {"near": {"lat": lat, "lon": lon, "meters": args.meters, "stations": near(lat, lon, args.meters)}}
    elif args.building:
        result = {"county": args.county, "building": building(args.county)}
    elif args.grew:
        result = {"county": args.county, "grew": grew(args.county)}
    else:
        result = {"county": args.county, "busiest": busiest(args.county)}
    result["credit"] = CREDIT
    if args.json:
        print(json.dumps(result, indent=2))
        raise SystemExit

    if "near" in result:
        n = result["near"]
        print(f"TxDOT count stations within {n['meters']:,} m of {n['lat']}, {n['lon']}:\n")
        for s in n["stations"] or []:
            print(f"  {s['vehicles_per_day']:>8,} a day ({s['year']})  {s['road']:<16} {s['station']}")
            print(f"  {'':>8}            {trend(s)}")
        if not n["stations"]:
            print("  None. TxDOT counts state roads: try a point on a highway, loop or farm-to-market road, or a bigger --meters.")
    elif "building" in result:
        b = result["building"]
        print(f"TxDOT's active projects, {args.county} County\n")
        for r in b["by_stage"]:
            print(f"  {(r['stage'] or 'unlisted'):<22}{r['projects']:>4} project{'s' if r['projects'] != 1 else ' '}  {money(r['cost']):>10}")
        print(f"  {'total':<22}{sum(r['projects'] for r in b['by_stage']):>4} projects   {money(sum(r['cost'] or 0 for r in b['by_stage'])):>10}")
        print("\nThe biggest:")
        for r in b["biggest"]:
            where = f"{r['from']} to {r['to']}" if r["to"] else r["from"]
            print(f"  {money(r['cost']):>9}  {r['highway']}, {where} · {r['stage']}")
            print(f"             {r['work']}")
        print("\nEstimated construction costs, as TxDOT lists them; stages change as projects move.")
    elif "grew" in result:
        print(f"Where traffic grew most since 2019, {args.county} County (stations carrying 10,000+ a day then):\n")
        for s in result["grew"]:
            print(f"  {s['change']:>+8,} a day ({s['change_pct']:+.0f}%)  {s['road']:<16} now {s['vehicles_per_day']:,}  {s['station']}")
    else:
        print(f"The busiest TxDOT count stations, {args.county} County ({result['busiest'][0]['year'] if result['busiest'] else ''}):\n")
        for s in result["busiest"]:
            print(f"  {s['vehicles_per_day']:>8,} a day  {s['road']:<16} {s['lat']:.5f}, {s['lon']:.5f}  {s['station']}")
        print("\nAADT: Annual Average Daily Traffic, vehicles both ways on an average day, estimated from counts.")
    print(f"\n{CREDIT}")
