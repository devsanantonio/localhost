"""Who represents me: every district a San Antonio address sits in, from City Council to Congress.

Bexar County maps every district people vote in: the voter precinct, the County
commissioner, the justice of the peace and constable, the Texas House and Senate,
the State Board of Education and Congress (redistricted for 2026), plus school
districts and the 2020 Census. The City maps its council districts. This asks
each map which district a point falls in, and names who holds the seat where the
map does.

    python3 main.py                                    # Geekdom, Houston and Soledad
    python3 main.py --address "100 Military Plaza, San Antonio, TX"
    python3 main.py --near 29.5200,-98.4000
    python3 main.py --json

Data: Bexar County Information Technology GIS; City of San Antonio Open Data, CC BY 4.0;
addresses located by the U.S. Census Bureau's geocoder.
"""
import argparse
import json
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

GEEKDOM = (29.42637, -98.49337)                          # Houston and Soledad
USER_AGENT = "devsa-localhost/1.0 (+https://github.com/devsanantonio/localhost)"
GEOCODER = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
BEXAR = "https://maps.bexar.org/arcgis/rest/services"
BEXAR_AGO = "https://services1.arcgis.com/8onVmslF2KXErTHT/arcgis/rest/services"
CITY_AGO = "https://services.arcgis.com/g1fRTDLeMgspWrYp/arcgis/rest/services"
CREDIT = ("Data: Bexar County Information Technology GIS; City of San Antonio Open Data, CC BY 4.0; "
          "address lookup: U.S. Census Bureau")
# Officeholders' names come from the County's maps, which are updated by hand and can lag an
# election by months or years: in November 2026 one still named a state representative who
# left office in 2023. The districts are what this is sure of, so names are printed as what
# "the map lists", never as fact, and the JSON calls them map_lists.
NAMES_NOTE = ("Names are what Bexar County's maps list, and can lag an election by years. Check one before you "
              "rely on it. Districts, results and your ballot: https://www.bexar.org/1568")

# label, layer, how to read the answer: a function of the feature's attributes
SEATS = [
    ("City Council", f"{CITY_AGO}/RedistrictedCouncilDistricts2022/FeatureServer/0",
     lambda a: (f"District {a['District']}", None)),
    ("County Commissioner", f"{BEXAR}/CommissionerPrecincts/MapServer/0",
     lambda a: (f"Precinct {a['Comm']}", a.get("ComName"))),
    ("Justice of the Peace", f"{BEXAR}/JusticeofthePeace/MapServer/1",
     lambda a: (f"Precinct {a['Precinct']}", a.get("Judges"))),
    ("Constable", f"{BEXAR}/Constables/MapServer/1",
     lambda a: (a["Precinct"], a.get("Constable"))),
    ("Texas House", f"{BEXAR_AGO}/TX_House_Reps_Redistricted/FeatureServer/0",
     lambda a: (f"District {a['District']}", a.get("STATE_REP"))),
    ("Texas Senate", f"{BEXAR_AGO}/TX_Senate_Redistricted/FeatureServer/0",
     lambda a: (f"District {a['District']}", a.get("SENATOR"))),
    ("State Board of Education", f"{BEXAR_AGO}/State_Board_of_Education_Redistricted/FeatureServer/0",
     lambda a: (f"District {a['District']}", None)),
    ("U.S. House", f"{BEXAR_AGO}/Bexar_County_US_Congressional_Districts/FeatureServer/0",
     lambda a: (f"Texas District {a['District']}", None)),
    ("School district", f"{BEXAR}/SchoolDistricts/MapServer/0",
     lambda a: (a["NAME"], None)),
    ("Voter precinct", f"{BEXAR}/EL/VoterPrecincts/MapServer/0",
     lambda a: (a["NAME"], None)),
]
BLOCK_GROUPS = f"{BEXAR}/CensusBlockGroups/MapServer/0"


def get(url, params, timeout=60):
    req = urllib.request.Request(f"{url}?{urllib.parse.urlencode(params)}", headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as res:
        return json.load(res)


def locate(address):
    """An address to a point, by the Census Bureau's geocoder: free, no key."""
    d = get(GEOCODER, {"address": address, "benchmark": "Public_AR_Current", "format": "json"})
    matches = d["result"]["addressMatches"]
    if not matches:
        raise SystemExit(f"The Census geocoder couldn't find {address!r}. Try adding the city and ZIP, or use --near lat,lon.")
    m = matches[0]
    return m["coordinates"]["y"], m["coordinates"]["x"], m["matchedAddress"]


UNAVAILABLE = object()


def at(url, lat, lon):
    """The attributes of the polygon a point falls in, None outside every polygon, or
    UNAVAILABLE if that map didn't answer in time: one slow server shouldn't sink the rest."""
    try:
        d = get(f"{url}/query", {"geometry": f"{lon},{lat}", "geometryType": "esriGeometryPoint", "inSR": 4326,
                                 "spatialRel": "esriSpatialRelIntersects", "outFields": "*", "returnGeometry": "false",
                                 "f": "json"}, timeout=20)
    except OSError:
        return UNAVAILABLE
    feats = d.get("features") or []
    return feats[0]["attributes"] if feats else None


def represents(lat, lon):
    with ThreadPoolExecutor(8) as pool:
        found = list(pool.map(lambda s: at(s[1], lat, lon), SEATS + [("", BLOCK_GROUPS, None)]))
    seats = []
    for (label, _, read), attrs in zip(SEATS, found):
        if attrs is UNAVAILABLE:
            seats.append({"seat": label, "district": "unavailable right now (that map didn't answer)", "map_lists": None})
            continue
        if attrs is None:
            # Outside the City's polygons means outside the city limits.
            seats.append({"seat": label, "district": "outside the city limits" if label == "City Council" else None, "map_lists": None})
            continue
        district, name = read(attrs)
        seats.append({"seat": label, "district": str(district).strip(), "map_lists": (name or "").strip() or None})
    bg = found[-1]
    census = {"block_group": bg["GEOID20"], "people_2020": int(bg["P1_001N"])} if bg and bg is not UNAVAILABLE else None
    return seats, census


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--address", help='a street address, e.g. "100 Military Plaza, San Antonio, TX"')
    ap.add_argument("--near", help="lat,lon (default: Geekdom, Houston and Soledad)")
    ap.add_argument("--json", action="store_true", help="print JSON instead of a list")
    args = ap.parse_args()

    where = None
    if args.address:
        lat, lon, where = locate(args.address)
    else:
        lat, lon = (float(x) for x in args.near.split(",")) if args.near else GEEKDOM
    seats, census = represents(lat, lon)

    if args.json:
        print(json.dumps({"point": [lat, lon], "address": where, "seats": seats, "census": census,
                          "note": NAMES_NOTE, "credit": CREDIT}, indent=2, ensure_ascii=False))
        raise SystemExit

    print(f"Who represents {where or f'{lat:.5f}, {lon:.5f}'}:\n")
    for s in seats:
        if s["district"] is None:
            continue
        print(f"  {s['seat']:<26}{s['district']}" + (f" · map lists {s['map_lists']}" if s["map_lists"] else ""))
    if census:
        print(f"\n  Census block group {census['block_group']}: {census['people_2020']:,} people in 2020")
    print(f"\n{NAMES_NOTE}")
    print(CREDIT)
