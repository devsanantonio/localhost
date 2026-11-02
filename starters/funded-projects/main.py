"""Where the region's road money is going, and which roads flood: the Alamo Area MPO's open data.

The Alamo Area Metropolitan Planning Organization decides which road and transit
projects across Bexar, Comal, Guadalupe and part of Kendall counties get federal
and state money. Its Transportation Improvement Program for 2027–2030 lists 68
funded projects with cost, year and agency. Its resilience study scores 6,372
road segments for how much of each floods. This asks both, and lets the server
do the adding up.

    python3 main.py                     # funded projects: totals by year and agency, then the biggest
    python3 main.py --county Bexar
    python3 main.py --flooding          # streets with the most road under a 100-year river flood
    python3 main.py --json

Data: Alamo Area Metropolitan Planning Organization
"""
import argparse
import json
import urllib.parse
import urllib.request

BASE = "https://services1.arcgis.com/ZmHtsY5M3DRYt09u/arcgis/rest/services"
TIP = f"{BASE}/TIP_2027_2030/FeatureServer/0/query"
ROADS = f"{BASE}/Roads_Exposure_Risk/FeatureServer/0/query"
CREDIT = "Data: Alamo Area Metropolitan Planning Organization"


def query(url, **params):
    params = {"where": "1=1", "returnGeometry": "false", "f": "json", **params}
    with urllib.request.urlopen(url + "?" + urllib.parse.urlencode(params), timeout=60) as res:
        data = json.load(res)
    if "error" in data:
        raise SystemExit(f"The service said: {data['error'].get('message', data['error'])}")
    return [f["attributes"] for f in data["features"]]


def projects(county):
    where = "(CANCELLED IS NULL OR CANCELLED = '')" + (f" AND COUNTY = '{county.replace(chr(39), '')}'" if county else "")
    total = [{"statisticType": "sum", "onStatisticField": "TOTAL_PROJECT", "outStatisticFieldName": "cost"},
             {"statisticType": "count", "onStatisticField": "OBJECTID", "outStatisticFieldName": "projects"}]
    by_year = query(TIP, where=where, groupByFieldsForStatistics="FisYear", outStatistics=json.dumps(total))
    by_agency = query(TIP, where=where, groupByFieldsForStatistics="SUBAGENCY", outStatistics=json.dumps(total))
    biggest = query(TIP, where=where, orderByFields="TOTAL_PROJECT DESC", resultRecordCount=10,
                    outFields="NAME,DescriptionPublic,TOTAL_PROJECT,FisYear,SUBAGENCY,COUNTY,LIMIT_FROM,LIMIT_TO")
    return {
        "by_year": sorted(({"year": r["FisYear"], "projects": r["projects"], "cost": r["cost"]} for r in by_year),
                          key=lambda r: r["year"] or 0),
        "by_agency": sorted(({"agency": r["SUBAGENCY"], "projects": r["projects"], "cost": r["cost"]} for r in by_agency),
                            key=lambda r: -(r["cost"] or 0)),
        "biggest": [{"road": r["NAME"], "what": (r["DescriptionPublic"] or "").strip(), "cost": r["TOTAL_PROJECT"],
                     "year": r["FisYear"], "agency": r["SUBAGENCY"], "county": r["COUNTY"],
                     "from": r["LIMIT_FROM"], "to": r["LIMIT_TO"]} for r in biggest],
    }


def flooding(limit=12):
    """Streets with the most length at least half-exposed to a 100-year river flood. The server sums it."""
    stats = [{"statisticType": "sum", "onStatisticField": "Shape__Length", "outStatisticFieldName": "length"},
             {"statisticType": "count", "onStatisticField": "OBJECTID", "outStatisticFieldName": "segments"}]
    rows = query(ROADS, where="Fluvial_100yr_PctExp >= 50 AND Street_Name IS NOT NULL",
                 groupByFieldsForStatistics="Street_Name", outStatistics=json.dumps(stats))
    rows.sort(key=lambda r: -r["length"])
    # The layer is in Texas South Central State Plane (EPSG 6588), so lengths are US survey feet.
    return [{"street": " ".join(r["Street_Name"].split()).title(), "segments": r["segments"],
             "miles": round(r["length"] / 5280, 2)} for r in rows[:limit]]


def money(n):
    return f"${n / 1e6:,.1f}M" if n else "$0"


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--county", help="Bexar, Comal, Guadalupe or Kendall")
    ap.add_argument("--flooding", action="store_true", help="streets most exposed to a 100-year river flood")
    ap.add_argument("--json", action="store_true", help="print JSON instead of tables")
    args = ap.parse_args()

    result = {"flooding": flooding()} if args.flooding else {"projects": projects(args.county)}
    result["credit"] = CREDIT
    if args.json:
        print(json.dumps(result, indent=2))
        raise SystemExit

    if args.flooding:
        print("Streets with the most road at least half under a 100-year river flood (Alamo Area MPO resilience study):\n")
        for r in result["flooding"]:
            print(f"  {r['miles']:>5.2f} mi  {r['segments']:>3} segment{'s' if r['segments'] != 1 else ' '}  {r['street']}")
        print("\nA model of exposure, not a forecast. For flood warnings: weather.gov/ewx and BexarFlood.org.")
    else:
        p = result["projects"]
        print("Funded projects, 2027–2030" + (f", {args.county} County" if args.county else "") + "\n")
        for r in p["by_year"]:
            print(f"  {r['year']}  {r['projects']:>3} project{'s' if r['projects'] != 1 else ' '}  {money(r['cost']):>10}")
        print()
        for r in p["by_agency"]:
            print(f"  {(r['agency'] or 'unlisted'):<22}{r['projects']:>3} project{'s' if r['projects'] != 1 else ' '}  {money(r['cost']):>10}")
        print("\nThe biggest:")
        for r in p["biggest"]:
            print(f"  {money(r['cost']):>9}  {r['year']}  {r['road']}, {r['from']} to {r['to']} ({r['county']}) · {r['agency']}")
            print(f"             {r['what']}")
    print(f"\n{CREDIT}")
