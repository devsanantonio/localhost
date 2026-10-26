"""What's being built near you: City of San Antonio building permits around a point.

The City publishes every permit it issues, with the work, the dates, the declared
value and the square footage. This asks its open-data API, in plain SQL, for the
permits issued near a point (Geekdom's corner, unless you give another), and
prints them biggest first, with how long each took to issue.

    python3 main.py
    python3 main.py --near 29.4216,-98.4767 --meters 60
    python3 main.py --since 2026-01-01

Data: City of San Antonio Open Data, CC BY 4.0
"""
import argparse
import datetime
import json
import math
import re
import statistics
import urllib.parse
import urllib.request

API = "https://data.sanantonio.gov/api/3/action/datastore_search_sql"
ISSUED = "c21106f9-3ef5-4f3a-8604-f992b4db7512"          # PERMITS ISSUED, 2025 to date
GEEKDOM = (29.42637, -98.49337)                          # Houston and Soledad
# Not building: left out, as on devsa.community/localhost.
NOT_BUILDING = ["Garage Sale", "Tree Affidavit Permit", "Tree Permit", "On Premise Sign", "Across the Street Banner",
                "Temporary Weekend Sign", "Feather Sign", "Avenue Sign", "Event Sign", "Inflatable Sign",
                "Off Premise Billboard", "Billboard Demolition"]
# Every permit also names a PRIMARY CONTACT, often a private person. This never asks for it.
FIELDS = '"PERMIT TYPE","WORK TYPE","PROJECT NAME","ADDRESS","DATE SUBMITTED","DATE ISSUED","DECLARED VALUATION","AREA (SF)"'


def sql(lat, lon, meters, since):
    dx, dy = meters / (111_320 * math.cos(math.radians(lat))), meters / 111_320
    return f'''SELECT {FIELDS} FROM "{ISSUED}"
WHERE "X_COORD" <> '' AND "Y_COORD" <> ''
  AND CAST("X_COORD" AS float) BETWEEN {lon - dx:.5f} AND {lon + dx:.5f}
  AND CAST("Y_COORD" AS float) BETWEEN {lat - dy:.5f} AND {lat + dy:.5f}
  AND "DATE ISSUED" >= '{since}'
  AND "PERMIT TYPE" NOT IN ({", ".join(f"'{t}'" for t in NOT_BUILDING)})'''


def fetch(query):
    with urllib.request.urlopen(f"{API}?{urllib.parse.urlencode({'sql': query})}", timeout=60) as res:
        body = json.load(res)
    if not body.get("success"):
        raise SystemExit(f"The City's API said no: {body.get('error')}")
    return body["result"]["records"]


def project(r):
    """ "AFF - 1231 E COMMERCE ST - Central at Commerce" -> "Central at Commerce". Commercial permits only."""
    raw = (r["PROJECT NAME"] or "").strip()
    if not (r["PERMIT TYPE"] or "").startswith("Comm") or re.search(r"building no|bldg|unit no", raw, re.I):
        return ""
    address = (r["ADDRESS"] or "").split(",")[0].strip().upper()
    parts = [p.strip() for p in re.split(r"\s+-\s*|-(?=[A-Z][a-z]|\d)", raw) if p.strip()]
    keep = [p for p in parts if not re.fullmatch(r"aff|sp|spl|sch|express|phased|complex plans|special projects?|minor structures", p, re.I)
            and not p[0].isdigit() and not address.startswith(p.upper())]
    return keep[-1] if keep else ""


def place(r):
    """Commercial permits by address; anything else by its block, since it may be someone's home."""
    street = (r["ADDRESS"] or "").split(",")[0].strip().title()
    if (r["PERMIT TYPE"] or "").startswith("Comm"):
        return street
    number, _, rest = street.partition(" ")
    return f"{int(number) // 100 * 100} block of {rest}" if number.isdigit() else street


def days(r):
    try:
        a, b = (datetime.date.fromisoformat(r[k][:10]) for k in ("DATE SUBMITTED", "DATE ISSUED"))
        return (b - a).days
    except (TypeError, ValueError):
        return None


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--near", help="lat,lon (default: Geekdom, Houston and Soledad)")
    ap.add_argument("--meters", type=int, default=150, help="how far to look, each way (default 150)")
    ap.add_argument("--since", default="2025-01-01", help="issued on or after, YYYY-MM-DD (the dataset starts 2025-01-01)")
    args = ap.parse_args()
    lat, lon = map(float, args.near.split(",")) if args.near else GEEKDOM

    rows = fetch(sql(lat, lon, args.meters, args.since))
    value = lambda r: float(r["DECLARED VALUATION"] or 0)
    rows.sort(key=lambda r: (-value(r), r["DATE ISSUED"] or ""))   # biggest first, then oldest
    print(f"{len(rows)} building permits within {args.meters} m of {lat:.5f}, {lon:.5f}, issued since {args.since}:\n")
    for r in rows[:15]:
        name = project(r)
        d = days(r)
        print(f"  {(r['DATE ISSUED'] or '')[:10]}  {(r['PERMIT TYPE'] or '').removesuffix(' Permit')}"
              + (f"  ${value(r):,.0f}" if value(r) else "") + f"  · {place(r)}"
              + (f"  · {name}" if name else "")
              + (f"  · issued in {d} days" if d is not None and d > 0 else "  · issued the day it was filed" if d == 0 else ""))
    if len(rows) > 15:
        print(f"  … and {len(rows) - 15} more")

    waits = [d for r in rows if (d := days(r)) is not None]
    if waits:
        print(f"\nMedian wait from filing to permit: {statistics.median(waits):.0f} days. "
              f"Declared value: ${sum(map(value, rows)):,.0f}.")
    print("Data: City of San Antonio Open Data, CC BY 4.0")
