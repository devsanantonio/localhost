"""Housing near you: Opportunity Home San Antonio's housing communities around a point.

Opportunity Home, the city's housing authority, publishes every community it owns
or partners on: public housing, affordable and mixed-income, who each is for, how
many homes and bedrooms, the year it was built, and whether residents get free
Wi-Fi. This lists the communities nearest a point (Geekdom's corner, unless you
give another), and can add the nearest VIA stop and how often a bus comes.

    python3 main.py
    python3 main.py --near 29.4110,-98.5200 --count 5
    python3 main.py --bus                # nearest VIA stop, and buses an hour within a quarter mile
    python3 main.py --districts          # communities and homes by council district
    python3 main.py --json

Data: Opportunity Home San Antonio. Bus stops: Data provided by VIA Metropolitan Transit.
"""
import argparse
import csv
import datetime
import io
import json
import math
import os
import sys
import urllib.parse
import urllib.request
import zipfile

SERVICE = ("https://services2.arcgis.com/nH68joXCaOE0Iiws/arcgis/rest/services/"
           "Housing_Communities/FeatureServer/19/query")
FIELDS = "DEVNAME,ADDRESS,PSTLZIP5,HSNGTYPE,HHOLDTYPE,TUNITS,BDRM0,BDRM1,BDRM2,BDRM3,BDRM4,BDRM5,BDRM6,YEARBUILT,OPSTATUS,OHSAWIFI,CNCLDST,ISD,WEBPAGE"
GEEKDOM = (29.42637, -98.49337)                          # Houston and Soledad
USER_AGENT = "devsa-localhost/1.0 (+https://github.com/devsanantonio/localhost)"
GTFS_URL = "https://www.viainfo.net/BusService/google_transit.zip"
HERE = os.path.dirname(os.path.abspath(__file__))
# Share the schedule via-next-bus already downloaded, if it's there.
ZIPS = [os.path.join(HERE, "..", "via-next-bus", "via_gtfs.zip"), os.path.join(HERE, "via_gtfs.zip")]
CREDIT = "Data: Opportunity Home San Antonio"
VIA_CREDIT = "Data provided by VIA Metropolitan Transit"
# The layer, as published, has a few rough edges. They're cleaned here, and said out loud
# when they apply, because a data problem you can name is one you can report.
TYPOS = {"Mixed-income Houseing": "Mixed-income Housing"}


def communities():
    params = {"where": "1=1", "outFields": FIELDS, "outSR": 4326, "f": "geojson"}
    req = urllib.request.Request(f"{SERVICE}?{urllib.parse.urlencode(params)}", headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as res:
        feats = json.load(res)["features"]
    out = []
    for f in feats:
        a, g = f["properties"], f.get("geometry")
        if not a.get("DEVNAME") or not g:
            continue                                     # one record is blank
        beds = {n: a.get(f"BDRM{n}") or 0 for n in range(7)}
        out.append({
            "name": a["DEVNAME"].strip(),
            "address": f"{(a.get('ADDRESS') or '').strip()}, {a.get('PSTLZIP5') or ''}".strip(", "),
            "type": TYPOS.get(a.get("HSNGTYPE"), a.get("HSNGTYPE")),
            "for": {"family": "families", "elderly/disabled": "seniors and people with disabilities"}.get(a.get("HHOLDTYPE"), a.get("HHOLDTYPE")),
            "homes": a.get("TUNITS") or 0,
            "bedrooms": {("studio" if n == 0 else f"{n}-bed"): c for n, c in beds.items() if c},
            "built": a.get("YEARBUILT"),
            "open": a.get("OPSTATUS") == "In Operations",
            "free_wifi": a.get("OHSAWIFI"),
            # "0" marks a community outside the city limits, which has no council district.
            "council_district": None if a.get("CNCLDST") in (None, "0") else int(a["CNCLDST"]),
            "school_district": a.get("ISD"),
            "lat": g["coordinates"][1], "lon": g["coordinates"][0],
        })
    return out


def meters(lat, lon, lat2, lon2):
    """Haversine distance in meters."""
    p1, p2 = math.radians(lat), math.radians(lat2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon) / 2) ** 2
    return 6_371_000 * 2 * math.asin(math.sqrt(a))


def schedule():
    for path in ZIPS:
        if os.path.exists(path):
            return zipfile.ZipFile(path)
    print("Downloading VIA's schedule (about 6 MB)…", file=sys.stderr)
    # VIA's server refuses Python's default user agent (403), so say who's asking.
    req = urllib.request.Request(GTFS_URL, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=120) as res, open(ZIPS[-1], "wb") as out:
        out.write(res.read())
    return zipfile.ZipFile(ZIPS[-1])


def rows(z, name):
    with z.open(name) as f:
        yield from csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig"))


WALK = 400   # a quarter mile, the usual distance people will walk to a bus


def add_buses(places):
    """For each place: its nearest VIA stop, and how many buses an hour stop within a quarter
    mile of it, 7 to 9 a.m. next Wednesday. Every stop in walking distance counts, not only
    the nearest (which can be one a route skips in the morning), and a bus that stops at two
    of them counts once."""
    z = schedule()
    stops = [(r["stop_id"], r["stop_name"], float(r["stop_lat"]), float(r["stop_lon"])) for r in rows(z, "stops.txt")]
    for p in places:
        dist = [(meters(p["lat"], p["lon"], s[2], s[3]), s) for s in stops]
        m, (sid, name, _, _) = min(dist)
        p["bus"] = {"nearest_stop": name, "meters": round(m), "stops_in_walking_distance": [s[0] for d, s in dist if d <= WALK]}
    day = datetime.date.today() + datetime.timedelta(days=(2 - datetime.date.today().weekday()) % 7 or 7)
    ymd, wd = day.strftime("%Y%m%d"), day.strftime("%A").lower()
    services = {r["service_id"] for r in rows(z, "calendar.txt") if r[wd] == "1" and r["start_date"] <= ymd <= r["end_date"]}
    if "calendar_dates.txt" in z.namelist():
        for r in rows(z, "calendar_dates.txt"):
            if r["date"] == ymd:
                (services.add if r["exception_type"] == "1" else services.discard)(r["service_id"])
    trips = {r["trip_id"]: r["route_id"] for r in rows(z, "trips.txt") if r["service_id"] in services}
    want = {s for p in places for s in p["bus"]["stops_in_walking_distance"]}
    at = {s: set() for s in want}                         # stop -> trips leaving it 7-9 a.m.
    for st in rows(z, "stop_times.txt"):
        # VIA writes early hours with a leading space (" 7:05:00"), so strip and pad before comparing.
        if st["stop_id"] in want and st["trip_id"] in trips and "07:00:00" <= st["departure_time"].strip().zfill(8) < "09:00:00":
            at[st["stop_id"]].add(st["trip_id"])
    for p in places:
        trips_near = set().union(*(at[s] for s in p["bus"]["stops_in_walking_distance"])) if p["bus"]["stops_in_walking_distance"] else set()
        p["bus"]["buses_per_hour_7_to_9am"] = round(len(trips_near) / 2, 1)
        p["bus"]["routes"] = len({trips[t] for t in trips_near})
        p["bus"]["stops_in_walking_distance"] = len(p["bus"]["stops_in_walking_distance"])
    return day


def by_district(all_places):
    d = {}
    for p in all_places:
        k = p["council_district"] or "outside the city"
        row = d.setdefault(k, {"council_district": k, "communities": 0, "homes": 0})
        row["communities"] += 1
        row["homes"] += p["homes"]
    return sorted(d.values(), key=lambda r: (isinstance(r["council_district"], str), r["council_district"] if isinstance(r["council_district"], int) else 99))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--near", help="lat,lon (default: Geekdom, Houston and Soledad)")
    ap.add_argument("--count", type=int, default=8, help="how many of the nearest to list (default 8)")
    ap.add_argument("--bus", action="store_true", help="add the nearest VIA stop, and weekday buses an hour within a quarter mile, 7-9 a.m.")
    ap.add_argument("--districts", action="store_true", help="communities and homes by council district")
    ap.add_argument("--json", action="store_true", help="print JSON instead of a list")
    args = ap.parse_args()

    lat, lon = (float(x) for x in args.near.split(",")) if args.near else GEEKDOM
    every = communities()

    if args.districts:
        rows_ = by_district(every)
        if args.json:
            print(json.dumps({"by_council_district": rows_, "credit": CREDIT}, indent=2))
            raise SystemExit
        print(f"Opportunity Home's {len(every)} communities, {sum(p['homes'] for p in every):,} homes, by council district:\n")
        for r in rows_:
            k = r["council_district"]
            print(f"  {('District ' + str(k)) if isinstance(k, int) else k:<20}{r['communities']:>4} communities{r['homes']:>8,} homes")
        print(f"\n{CREDIT}")
        raise SystemExit

    for p in every:
        p["meters"] = round(meters(lat, lon, p["lat"], p["lon"]))
    near = sorted(every, key=lambda p: p["meters"])[: args.count]
    day = add_buses(near) if args.bus else None

    if args.json:
        print(json.dumps({"near": [lat, lon], "communities": near, "buses_on": day.isoformat() if day else None,
                          "credit": CREDIT + (f"; {VIA_CREDIT}" if day else "")}, indent=2))
        raise SystemExit

    print(f"The {len(near)} Opportunity Home communities nearest {lat:.5f}, {lon:.5f} (of {len(every)}):\n")
    for p in near:
        km = f"{p['meters'] / 1000:.1f} km" if p["meters"] >= 1000 else f"{p['meters']} m"
        beds = ", ".join(f"{c} {k}" for k, c in p["bedrooms"].items())
        print(f"  {p['name']}  ({km})")
        print(f"    {p['type'] or 'Housing'} for {p['for'] or 'residents'} · {p['homes']} homes" + (f" ({beds})" if beds else "")
              + (f" · built {p['built']}" if p["built"] else "") + ("" if p["open"] else " · coming soon"))
        extra = [f"council district {p['council_district']}" if p["council_district"] else "outside the city limits",
                 p["school_district"] or "", "free Wi-Fi" if p["free_wifi"] == "Yes" else ""]
        print("    " + " · ".join(x for x in extra if x))
        if day:
            b = p["bus"]
            print(f"    nearest stop: {b['nearest_stop']}, {b['meters']} m · within a quarter mile, 7-9 a.m.:"
                  f" {b['buses_per_hour_7_to_9am']:g} buses an hour on {b['routes']} route{'s' if b['routes'] != 1 else ''}")
        print()
    if day:
        print(f"Buses counted from VIA's schedule for {day:%A, %B %-d}.")
    print(CREDIT + (f". Bus stops: {VIA_CREDIT}." if day else ""))
