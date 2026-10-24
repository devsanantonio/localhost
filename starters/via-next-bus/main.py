"""The next buses from a VIA stop, from VIA's published schedule (GTFS).

    python3 main.py "houston & st mary"
    python3 main.py "medical & babcock" --count 15

The first run downloads VIA's schedule (about 6 MB) and keeps it next to this
file as via_gtfs.zip. Delete that file to fetch a fresh copy; VIA publishes a
new schedule a few times a year.

This is the *scheduled* time. VIA also publishes realtime vehicle positions and
trip updates (GTFS-realtime); see README.md for where to take that next.

Data provided by VIA Metropolitan Transit
"""
import argparse
import csv
import io
import os
import urllib.request
import zipfile
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

GTFS_URL = "https://www.viainfo.net/BusService/google_transit.zip"
HERE = os.path.dirname(os.path.abspath(__file__))
ZIP = os.path.join(HERE, "via_gtfs.zip")
TZ = ZoneInfo("America/Chicago")


def rows(z, name):
    with z.open(name) as f:
        yield from csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig"))


def schedule():
    if not os.path.exists(ZIP):
        print("Downloading VIA's schedule (about 6 MB)…")
        urllib.request.urlretrieve(GTFS_URL, ZIP)
    return zipfile.ZipFile(ZIP)


def services_running(z, day):
    """The service_ids that run on `day`: the weekly calendar, then the day's exceptions."""
    ymd, weekday = day.strftime("%Y%m%d"), day.strftime("%A").lower()
    running = {
        r["service_id"] for r in rows(z, "calendar.txt")
        if r[weekday] == "1" and r["start_date"] <= ymd <= r["end_date"]
    }
    if "calendar_dates.txt" in z.namelist():
        for r in rows(z, "calendar_dates.txt"):
            if r["date"] == ymd:
                (running.add if r["exception_type"] == "1" else running.discard)(r["service_id"])
    return running


def next_departures(z, stop_ids, now, count):
    routes = {r["route_id"]: r for r in rows(z, "routes.txt")}
    found = []
    # Today's late-night trips are listed under yesterday's service with times past
    # 24:00, so both days are checked.
    for offset in (-1, 0):
        day = (now + timedelta(days=offset)).date()
        midnight = datetime(day.year, day.month, day.day, tzinfo=TZ)
        services = services_running(z, day)
        trips = {r["trip_id"]: r for r in rows(z, "trips.txt") if r["service_id"] in services}
        for st in rows(z, "stop_times.txt"):
            if st["stop_id"] not in stop_ids or st["trip_id"] not in trips:
                continue
            h, m, s = (int(x) for x in st["departure_time"].split(":"))
            when = midnight + timedelta(hours=h, minutes=m, seconds=s)
            if when >= now:
                trip = trips[st["trip_id"]]
                found.append((when, routes[trip["route_id"]], trip.get("trip_headsign", ""), st["stop_id"]))
    return sorted(found, key=lambda x: x[0])[:count]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="The next buses from a VIA stop.")
    parser.add_argument("stop", help='part of a stop name, e.g. "houston & st mary"')
    parser.add_argument("--count", type=int, default=10)
    args = parser.parse_args()

    z = schedule()
    words = args.stop.upper().replace("&", " & ").split()
    stops = {r["stop_id"]: r for r in rows(z, "stops.txt") if all(w in r["stop_name"].upper() for w in words)}
    if not stops:
        raise SystemExit(f'No stop name contains "{args.stop}". Try fewer words, like a single street.')
    if len(stops) > 12:
        names = sorted({s["stop_name"] for s in stops.values()})
        raise SystemExit(f"{len(stops)} stops match. Be more specific. Some of them:\n  " + "\n  ".join(names[:12]))

    now = datetime.now(TZ)
    print(f"Next buses from {len(stops)} stop(s) matching \"{args.stop}\", after {now:%-I:%M %p}:\n")
    for when, route, headsign, stop_id in next_departures(z, set(stops), now, args.count):
        name = route["route_short_name"] or route["route_long_name"]
        print(f"  {when:%-I:%M %p}  Route {name:<5} {headsign:<34} at {stops[stop_id]['stop_name']}")
    print("\nScheduled times. Data provided by VIA Metropolitan Transit")
