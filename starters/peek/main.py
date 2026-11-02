"""Peek at any San Antonio map layer, or find one, without knowing anything first.

Most of San Antonio's public agencies publish their data the same way, as
ArcGIS layers that answer the same questions. Give this any layer's address and
it tells you what's in it: how many rows, when it last changed, its fields and
a few real rows. Or search every publisher at once for a word.

    python3 main.py --find flood
    python3 main.py https://services1.arcgis.com/ZmHtsY5M3DRYt09u/arcgis/rest/services/Roads_Exposure_Risk/FeatureServer/0
    python3 main.py https://services1.arcgis.com/ZmHtsY5M3DRYt09u/arcgis/rest/services/Roads_Exposure_Risk/FeatureServer
    python3 main.py --all          # every public layer of every publisher, counted
    python3 main.py --find flood --json

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


def public_layers(q, limit=None):
    """Public layer items from ArcGIS search, newest first, with survey and feedback layers left out.

    Survey and feedback layers hold what people submitted through a form, sometimes with
    names and addresses. The filter is by name and keyword, so it can miss one.
    """
    results, start = [], 1
    while start > 0 and (limit is None or len(results) < limit):
        data = get("https://www.arcgis.com/sharing/rest/search", q=q, num=100, start=start,
                   sortField="modified", sortOrder="desc")
        results += [
            r for r in data["results"]
            if r.get("access") == "public" and r.get("url")
            and not any("survey123" in k.lower() for k in r.get("typeKeywords", []))
            and not re.search(r"_(form|results|fieldworker|stakeholder)$|survey|participant|feedback|comment|crowdsource|application", r["title"], re.I)
        ]
        start = data.get("nextStart", -1)
    return results[:limit] if limit else results


def item(r, org=None):
    # When the search was scoped to one publisher, that is the owner, even if the layer is served
    # from another host. Otherwise the address says whose it is.
    name, credit = PUBLISHERS.get(org) or publisher(r["url"] + "/")
    return {"title": r["title"], "publisher": name, "url": r["url"], "type": r.get("type"),
            "modified": datetime.fromtimestamp(r["modified"] / 1000, tz=timezone.utc).date().isoformat(),
            "summary": short(r.get("snippet") or "", 200) or None, "credit": credit}


def find(word):
    """Search every publisher's public layers for a word, newest first."""
    orgs = " OR ".join(f"orgid:{org}" for org in PUBLISHERS)
    return [item(r) for r in public_layers(f'{word} AND ({orgs}) AND (type:"Feature Service" OR type:"Map Service")', 50)]


def everything():
    """Every public layer of every publisher: the whole catalog, grouped by who publishes it."""
    out, seen = [], set()
    for org in PUBLISHERS:
        for r in public_layers(f'orgid:{org} AND (type:"Feature Service" OR type:"Map Service")'):
            if r["url"] not in seen:
                seen.add(r["url"])
                out.append(item(r, org))
    return out


def service(url, info):
    """A service holds one or more layers. List them."""
    return {"service": url, "description": short(info.get("serviceDescription") or info.get("description") or "", 300) or None,
            "layers": [{"id": l["id"], "name": l["name"], "url": f"{url.rstrip('/')}/{l['id']}"}
                       for l in info.get("layers", []) + info.get("tables", [])]}


def layer(url, info, rows):
    name, credit = publisher(url)
    count = get(url + "/query", where="1=1", returnCountOnly="true").get("count")
    sample = get(url + "/query", where="1=1", outFields="*", returnGeometry="false", resultRecordCount=rows)
    return {
        "layer": info.get("name"), "url": url, "publisher": name, "rows": count,
        "last_changed": day((info.get("editingInfo") or {}).get("lastEditDate")),
        "geometry": info.get("geometryType", "none").replace("esriGeometry", "").lower(),
        "description": short(re.sub(r"<[^>]+>", " ", info["description"]), 300) if info.get("description") else None,
        "fields": [{"name": f["name"], "type": f["type"].replace("esriFieldType", "").lower()} for f in info.get("fields", [])],
        "sample": [{k: v for k, v in f["attributes"].items() if v not in (None, "", " ")} for f in sample["features"][:rows]],
        "credit": credit, "layer_credit": info.get("copyrightText") or None,
    }


def show(result, args):
    if args.find:
        print(f'{len(result)} public layers mention "{args.find}", newest first (survey responses left out):\n')
        for r in result:
            print(f"{datetime.fromisoformat(r['modified']).strftime('%b %-d, %Y'):<14}{r['publisher']:<30}{short(r['title'], 56)}")
            print(f"{'':<14}{r['url']}\n")
        print("Peek at one: python3 main.py <address>")
    elif args.all:
        by = {}
        for r in result:
            by[r["publisher"]] = by.get(r["publisher"], 0) + 1
        print(f"{len(result)} public layers across {len(by)} publishers:\n")
        for name, n in sorted(by.items(), key=lambda kv: -kv[1]):
            print(f"  {n:>5}  {name}")
        print("\nThe full list: python3 main.py --all --json")
    elif "layers" in result:
        print(f"{result['description'] or 'A service'}\n")
        for l in result["layers"]:
            print(f"  {l['url']}   {l['name']}")
        print("\nPeek at one: python3 main.py <address>")
    else:
        print(result["layer"] or "Layer", f"· {result['publisher']}")
        print(f"{result['rows']:,} rows · last changed {result['last_changed']} · {result['geometry'] or 'no map shape'}")
        if result["description"]:
            print(result["description"])
        print("\nFields")
        for f in result["fields"]:
            print(f"  {f['name']:<32}{f['type']}")
        n = len(result["sample"])
        print(f"\nFirst {n} row" + ("s" if n != 1 else ""))
        for row in result["sample"]:
            print("  " + " · ".join(f"{k}: {short(v, 40)}" for k, v in list(row.items())[:8]))
        print(f"\n{result['credit']}")
        if result["layer_credit"]:
            print(f"The layer adds: {short(result['layer_credit'], 200)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("address", nargs="?", help="a layer or service address (…/FeatureServer/0 or …/MapServer)")
    parser.add_argument("--find", metavar="WORD", help="search every publisher's layers for a word")
    parser.add_argument("--all", action="store_true", help="list every public layer of every publisher")
    parser.add_argument("--rows", type=int, default=5, help="how many rows to show (default 5)")
    parser.add_argument("--json", action="store_true", help="print JSON instead of text")
    args = parser.parse_args()

    if args.find:
        result = find(args.find)
    elif args.all:
        result = everything()
    elif args.address:
        url = args.address.split("?")[0].rstrip("/")
        info = get(url)
        result = layer(url, info, args.rows) if "fields" in info else service(url, info)
    else:
        parser.print_help()
        raise SystemExit
    print(json.dumps(result, indent=2)) if args.json else show(result, args)
