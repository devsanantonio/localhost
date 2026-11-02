"""The Edwards Aquifer today: San Antonio's water, from the J-17 index well and the springs.

Most of San Antonio's water comes from the Edwards Aquifer. The Edwards Aquifer
Authority measures it every 15 minutes at the J-17 index well in Bexar County,
and the U.S. Geological Survey measures what flows out at Comal and San Marcos
Springs. This prints the latest level, its 10-day average (what the authority's
drought rules are written against), and the springflow.

    python3 main.py
    python3 main.py --days 30
    python3 main.py --json

The well's readings are provisional until the authority approves them. For the
official drought stage, see edwardsaquifer.org.

Data: Edwards Aquifer Authority
Data: U.S. Geological Survey
"""
import argparse
import csv
import io
import json
import urllib.parse
import urllib.request
from datetime import datetime, timedelta

# The authority's CSV for J-17: every 15-minute reading since 1992, newest first.
# It is about 57 MB in all, so this reads only the newest lines and stops.
J17 = "https://data.edwardsaquifer.org/GroundWater/DownloadGroundwaterCsv?siteId=J17WL&sensorName=WLE"
USGS_DAILY = "https://waterservices.usgs.gov/nwis/dv/"
SPRINGS = {"08168710": "Comal Springs", "08170000": "San Marcos Springs"}

# J-17's stage triggers for the San Antonio Pool, in feet above sea level, applied
# to the 10-day average. The authority also uses springflow, so the official stage
# can differ: this is the well's side of it only.
STAGES = [(660, "I"), (650, "II"), (640, "III"), (630, "IV"), (625, "V")]


def j17(days):
    """Readings from the last `days` days, newest first, read straight off the stream."""
    rows, cutoff = [], None
    with urllib.request.urlopen(J17, timeout=120) as res:
        lines = (line for line in io.TextIOWrapper(res, encoding="utf-8-sig") if not line.startswith("#"))
        for r in csv.DictReader(lines):
            when = datetime.strptime(r["dt_CST"], "%Y-%m-%d %H:%M:%S")
            cutoff = cutoff or when - timedelta(days=days)
            if when < cutoff:
                break
            if r["WLE"]:
                rows.append((when, float(r["WLE"]), r["MeasStatus"]))
    return rows


def stage(level):
    """The J-17 trigger the level is below, if any (the lowest wins)."""
    hit = None
    for threshold, name in STAGES:
        if level < threshold:
            hit = (name, threshold)
    return hit


def springflow():
    data = json.load(urllib.request.urlopen(USGS_DAILY + "?" + urllib.parse.urlencode(
        {"format": "json", "sites": ",".join(SPRINGS), "parameterCd": "00060", "period": "P10D"}), timeout=60))
    out = []
    for ts in data["value"]["timeSeries"]:
        site = ts["sourceInfo"]["siteCode"][0]["value"]
        values = ts["values"][0]["value"]
        if values:
            out.append({"site": site, "name": SPRINGS.get(site, ts["sourceInfo"]["siteName"]),
                        "flow_cfs": float(values[-1]["value"]), "date": values[-1]["dateTime"][:10]})
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--days", type=int, default=10, help="how many days of J-17 readings to average (default 10)")
    ap.add_argument("--json", action="store_true", help="print JSON instead of text")
    args = ap.parse_args()

    readings = j17(args.days)
    if not readings:
        raise SystemExit("No J-17 readings came back. The authority's site may be down; try again later.")
    latest_when, latest, status = readings[0]
    average = sum(r[1] for r in readings) / len(readings)
    trigger = stage(average) if args.days == 10 else None
    result = {
        "j17": {"level_ft": latest, "as_of": latest_when.isoformat(), "status": status,
                "average_ft": round(average, 2), "average_days": args.days,
                "low_ft": min(r[1] for r in readings), "high_ft": max(r[1] for r in readings),
                "stage_trigger": {"stage": trigger[0], "below_ft": trigger[1]} if trigger else None},
        "springs": springflow(),
        "credit": ["Data: Edwards Aquifer Authority", "Data: U.S. Geological Survey"],
    }

    if args.json:
        print(json.dumps(result, indent=2))
        raise SystemExit

    w = result["j17"]
    print(f"J-17 index well, Bexar County · {latest_when:%b %-d, %Y %-I:%M %p} CST"
          + (" (provisional)" if status == "P" else ""))
    print(f"  level           {latest:.2f} ft above sea level")
    print(f"  {args.days}-day average  {w['average_ft']:.2f} ft   (range {w['low_ft']:.2f}–{w['high_ft']:.2f})")
    if args.days == 10:
        print(f"  by J-17 alone   Stage {trigger[0]}: the 10-day average is below {trigger[1]} ft" if trigger
              else "  by J-17 alone   above every drought trigger (660 ft and up)")
        print("                  The authority also weighs springflow. Official stage: edwardsaquifer.org")
    print("\nSpringflow, daily")
    for s in result["springs"]:
        print(f"  {s['name']:<20}{s['flow_cfs']:>8,.0f} cfs   {s['date']}")
    print()
    print("\n".join(result["credit"]))
