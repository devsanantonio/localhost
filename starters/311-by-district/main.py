"""311 calls by council district, from the City of San Antonio's open data.

Asks the City's live 311 feature service to do the counting, so nothing is
downloaded: one request per question, answered in a second or two.

    python3 main.py                 # every district: calls, and how many closed late
    python3 main.py --district 5    # one district: what people call 311 about

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

    print(f"{'District':<10}{'Calls':>10}{'Closed late':>14}")
    for d in sorted(counts, key=lambda d: (d == 0, d)):
        c = counts[d]
        total = c["YES"] + c["NO"]
        label = "none" if d == 0 else str(d)
        print(f"{label:<10}{total:>10,}{c['YES'] / total:>13.0%}")
    print("\n'none' is calls recorded with council district 0, meaning no district was assigned.")


def one_district(district):
    rows = stats("Category", where=f"CouncilDistrict = {int(district)}")
    rows.sort(key=lambda r: r["calls"], reverse=True)
    total = sum(r["calls"] for r in rows)
    print(f"District {district}: {total:,} calls\n")
    for r in rows:
        print(f"{r['calls']:>8,}  {r['calls'] / total:>4.0%}  {r['Category']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--district", type=int, choices=range(1, 11), help="show one district by category")
    args = parser.parse_args()

    first, last = date_range()
    print(f"San Antonio 311 calls opened {first} – {last}\n")
    one_district(args.district) if args.district else by_district()
    print("\nData: City of San Antonio Open Data, CC BY 4.0")
