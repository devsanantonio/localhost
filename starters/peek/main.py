"""Peek at any San Antonio map layer, or find one, without knowing anything first.

Most of San Antonio's public agencies publish their data the same way, as
ArcGIS layers that answer the same questions. Give this any layer's address and
it tells you what's in it: how many rows, when it last changed, its fields and
a few real rows. Or search every publisher at once for a word.

    python3 main.py --find flood
    python3 main.py https://services1.arcgis.com/ZmHtsY5M3DRYt09u/arcgis/rest/services/Roads_Exposure_Risk/FeatureServer/0
    python3 main.py https://services1.arcgis.com/ZmHtsY5M3DRYt09u/arcgis/rest/services/Roads_Exposure_Risk/FeatureServer

Each layer belongs to its publisher and carries its own terms. This prints the
publisher's credit line; read SOURCES.md and ATTRIBUTION.md before you publish.
"""
import argparse
import json
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone

# Who publishes San Antonio's data on ArcGIS, by organization id. The id is the
# part of a layer's address after services*.arcgis.com/, so a layer's address
# says whose it is. Credit lines are the ones in ATTRIBUTION.md.
PUBLISHERS = {
    "g1fRTDLeMgspWrYp": ("City of San Antonio", "Data: City of San Antonio Open Data, CC BY 4.0"),
    "8onVmslF2KXErTHT": ("Bexar County", "Data: Bexar County Information Technology GIS"),
    "Eb8y2VjBgkqbQJwk": (
        "San Antonio River Authority",
        "This uses River Authority's data but is not endorsed or verified by River Authority. (Add the date you retrieved it.)",
    ),
    "ZmHtsY5M3DRYt09u": ("Alamo Area MPO", "Data: Alamo Area Metropolitan Planning Organization"),
    "nH68joXCaOE0Iiws": ("Opportunity Home San Antonio", "Data: Opportunity Home San Antonio"),
    "p0kPTvyvhLmiT5Ha": ("Edwards Aquifer Authority", "Data: Edwards Aquifer Authority"),
}
# Bexar County also serves layers from its own server, outside ArcGIS Online.
HOSTS = {"maps.bexar.org": "8onVmslF2KXErTHT"}


def get(url, **params):
    params["f"] = "json"
    with urllib.request.urlopen(url + "?" + urllib.parse.urlencode(params), timeout=60) as res:
        data = json.load(res)
    if "error" in data:
        raise SystemExit(f"The service said: {data['error'].get('message', data['error'])}")
    return data


def publisher(url):
    m = re.search(r"arcgis\.com/([A-Za-z0-9]{16})/", url)
    org = m.group(1) if m else HOSTS.get(urllib.parse.urlparse(url).hostname)
    return PUBLISHERS.get(org, ("an unlisted publisher", "Check the layer's description for how to credit it."))


def day(ms):
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%b %-d, %Y") if ms else "unknown"


def short(value, width=60):
    text = re.sub(r"\s+", " ", str(value)).strip()
    return text if len(text) <= width else text[: width - 1] + "…"


def find(word):
    """Search every publisher's public layers for a word, newest first."""
    orgs = " OR ".join(f"orgid:{org}" for org in PUBLISHERS)
    q = f'{word} AND ({orgs}) AND (type:"Feature Service" OR type:"Map Service")'
    data = get("https://www.arcgis.com/sharing/rest/search", q=q, num=50, sortField="modified", sortOrder="desc")
    # Survey and feedback layers hold what people submitted through a form, sometimes
    # with names and addresses. Leave them out. (The filter is by name, so it can miss one.)
    results = [
        r for r in data["results"]
        if r.get("access") == "public" and r.get("url")
        and not any("survey123" in k.lower() for k in r.get("typeKeywords", []))
        and not re.search(r"_(form|results|fieldworker|stakeholder)$|survey|participant|feedback|comment|crowdsource|application", r["title"], re.I)
    ]
    print(f'{len(results)} public layers mention "{word}", newest first (survey responses left out):\n')
    for r in results:
        name, _ = publisher(r["url"] + "/")
        print(f"{day(r['modified']):<14}{name:<30}{short(r['title'], 56)}")
        print(f"{'':<14}{r['url']}\n")
    print("Peek at one: python3 main.py <address>")


def service(url, info):
    """A service holds one or more layers. List them."""
    print(f"{short(info.get('serviceDescription') or info.get('description') or 'A service', 200)}\n")
    for layer in info.get("layers", []) + info.get("tables", []):
        print(f"  {url.rstrip('/')}/{layer['id']}   {layer['name']}")
    print("\nPeek at one: python3 main.py <address>")


def layer(url, info, rows):
    name, credit = publisher(url)
    count = get(url + "/query", where="1=1", returnCountOnly="true").get("count")
    edited = (info.get("editingInfo") or {}).get("lastEditDate")
    print(info.get("name", "Layer"), f"· {name}")
    print(f"{count:,} rows · last changed {day(edited)} · {info.get('geometryType', 'no map shape').replace('esriGeometry', '').lower()}")
    if info.get("description"):
        print(short(re.sub(r"<[^>]+>", " ", info["description"]), 300))

    print("\nFields")
    for f in info.get("fields", []):
        print(f"  {f['name']:<32}{f['type'].replace('esriFieldType', '').lower()}")

    sample = get(url + "/query", where="1=1", outFields="*", returnGeometry="false", resultRecordCount=rows)
    n = len(sample["features"])
    print(f"\nFirst {n} row" + ("s" if n != 1 else ""))
    for feature in sample["features"][:rows]:
        filled = {k: v for k, v in feature["attributes"].items() if v not in (None, "", " ")}
        print("  " + " · ".join(f"{k}: {short(v, 40)}" for k, v in list(filled.items())[:8]))

    print(f"\n{credit}")
    if info.get("copyrightText"):
        print(f"The layer adds: {short(info['copyrightText'], 200)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("address", nargs="?", help="a layer or service address (…/FeatureServer/0 or …/MapServer)")
    parser.add_argument("--find", metavar="WORD", help="search every publisher's layers for a word")
    parser.add_argument("--rows", type=int, default=5, help="how many rows to show (default 5)")
    args = parser.parse_args()

    if args.find:
        find(args.find)
    elif args.address:
        url = args.address.split("?")[0].rstrip("/")
        info = get(url)
        layer(url, info, args.rows) if "fields" in info else service(url, info)
    else:
        parser.print_help()
