"""311 calls by council district, from the City of San Antonio's open data.

Asks the City's live 311 feature service to do the counting, so nothing is
downloaded: one request per question, answered in a second or two.

    python3 main.py                 # every district: calls, and how many closed late
    python3 main.py --district 5    # one district: what people call 311 about
    python3 main.py --json          # the same, as JSON

Data: City of San Antonio Open Data, CC BY 4.0
"""
import argparse
import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone

SERVICE = (
    "https://services.arcgis.com/g1fRTDLeMgspWrYp/arcgis/rest/services/"
    "311_All_Service_Calls/FeatureServer/0/query"
)


def query(**params):
    params.setdefault("where", "1=1")
    params["f"] = "json"
    url = SERVICE + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=60) as res:
        data = json.load(res)
    if "error" in data:
        raise SystemExit(f"The service said: {data['error']}")
    return [f["attributes"] for f in data["features"]]


def stats(group_by, where="1=1"):
    """Count calls grouped by one or more fields. The server does the work."""
    count = [{"statisticType": "count", "onStatisticField": "OBJECTID", "outStatisticFieldName": "calls"}]
    return query(where=where, groupByFieldsForStatistics=group_by, outStatistics=json.dumps(count))


def date_range():
    rows = query(outStatistics=json.dumps([
        {"statisticType": "min", "onStatisticField": "OpenedDateTime", "outStatisticFieldName": "first"},
        {"statisticType": "max", "onStatisticField": "OpenedDateTime", "outStatisticFieldName": "last"},
    ]))
    day = lambda ms: datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%b %-d, %Y")
    return day(rows[0]["first"]), day(rows[0]["last"])


def by_district():
    counts = {}
    for row in stats("CouncilDistrict,LateYesNo"):
        d = row["CouncilDistrict"]
        counts.setdefault(d, {"YES": 0, "NO": 0})[row["LateYesNo"] or "NO"] += row["calls"]
    return [{"district": d or None, "calls": c["YES"] + c["NO"], "closed_late": c["YES"],
             "late_share": round(c["YES"] / (c["YES"] + c["NO"]), 3)}
            for d, c in sorted(counts.items(), key=lambda kv: (kv[0] == 0, kv[0]))]


def one_district(district):
    rows = stats("Category", where=f"CouncilDistrict = {int(district)}")
    rows.sort(key=lambda r: r["calls"], reverse=True)
    return [{"category": r["Category"], "calls": r["calls"]} for r in rows]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--district", type=int, choices=range(1, 11), help="show one district by category")
    parser.add_argument("--json", action="store_true", help="print JSON instead of a table")
    args = parser.parse_args()

    first, last = date_range()
    rows = one_district(args.district) if args.district else by_district()
    if args.json:
        key = "categories" if args.district else "districts"
        print(json.dumps({"opened": {"from": first, "to": last}, "district": args.district, key: rows,
                          "credit": "Data: City of San Antonio Open Data, CC BY 4.0"}, indent=2))
        raise SystemExit

    print(f"San Antonio 311 calls opened {first} – {last}\n")
    if args.district:
        total = sum(r["calls"] for r in rows)
        print(f"District {args.district}: {total:,} calls\n")
        for r in rows:
            print(f"{r['calls']:>8,}  {r['calls'] / total:>4.0%}  {r['category']}")
    else:
        print(f"{'District':<10}{'Calls':>10}{'Closed late':>14}")
        for r in rows:
            print(f"{str(r['district'] or 'none'):<10}{r['calls']:>10,}{r['late_share']:>13.0%}")
        print("\n'none' is calls recorded with council district 0, meaning no district was assigned.")
    print("\nData: City of San Antonio Open Data, CC BY 4.0")
