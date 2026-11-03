"""How San Antonio compares: the economy against seven peer metros, from the City's own tables.

The City's Economic Development Department publishes San Antonio beside seven
peer metros (Austin, Charlotte, Dallas, Houston, Jacksonville, Phoenix and San
Diego): how fast each economy has grown, how much of it comes from the
industries San Antonio is betting on, who owns its businesses, and what its
colleges graduate. This asks the City's open-data API in SQL and ranks them.

    python3 main.py                 # GDP growth since 2020, and San Antonio's target industries
    python3 main.py --owners        # share of businesses owned by Hispanic, women and veteran owners
    python3 main.py --graduates     # graduates by program, San Antonio against the peer average
    python3 main.py --json

Data: City of San Antonio Open Data, CC BY 4.0
"""
import argparse
import json
import urllib.parse
import urllib.request

API = "https://data.sanantonio.gov/api/3/action/datastore_search_sql"
GDP = "d2bb4061-c120-494a-831c-de17ead8d993"          # GDP SATX and Peer
OWNERS = "3887eb46-bc75-42ee-9802-9322452c4b0a"       # Firm Ownership
GRADUATES = "8440e05b-409b-48e5-87ca-673a77317d1b"    # Graduates SATX and Peers
CREDIT = "Data: City of San Antonio Open Data, CC BY 4.0"
HOME = "San Antonio"


def sql(query):
    with urllib.request.urlopen(f"{API}?{urllib.parse.urlencode({'sql': query})}", timeout=60) as res:
        body = json.load(res)
    if not body.get("success"):
        raise SystemExit(f"The City's API said no: {body.get('error')}")
    return body["result"]["records"]


def growth():
    """Each metro's GDP from its first year to its latest, ranked by growth."""
    rows = sql(f'SELECT "MSA", "Year", "GDP" FROM "{GDP}" WHERE "Category" = \'Overall\' ORDER BY "Year"')
    by = {}
    for r in rows:
        by.setdefault(r["MSA"], []).append((r["Year"], float(r["GDP"])))
    out = []
    for msa, years in by.items():
        (y0, g0), (y1, g1) = years[0], years[-1]
        out.append({"metro": msa, "from": y0, "to": y1, "gdp_from": g0, "gdp_to": g1, "growth": round(g1 / g0 - 1, 4)})
    return sorted(out, key=lambda r: -r["growth"])


def industries():
    """San Antonio's GDP in the industry clusters the City targets, in the latest year published."""
    rows = sql(f'SELECT "Category", "Year", "GDP" FROM "{GDP}" WHERE "MSA" = \'{HOME}\' AND "Category" <> \'Overall\' ORDER BY "Year"')
    by = {}
    for r in rows:
        by.setdefault(r["Category"], []).append((r["Year"], float(r["GDP"])))
    # The clusters may have only one year published; growth is None until there are two.
    return sorted(({"industry": c, "year": v[-1][0], "gdp": v[-1][1], "growth_since": v[0][0] if len(v) > 1 else None,
                    "growth": round(v[-1][1] / v[0][1] - 1, 4) if len(v) > 1 else None} for c, v in by.items()),
                  key=lambda r: -r["gdp"])


def owners():
    """Share of each metro's businesses with Hispanic, women or veteran owners."""
    rows = sql(f'SELECT "MSA", "Metric", "Overall" FROM "{OWNERS}" WHERE "Metric" IN (\'Overall\', \'Hispanic\', \'Female\', \'Veteran\')')
    by = {}
    for r in rows:
        by.setdefault(r["MSA"], {})[r["Metric"]] = float(r["Overall"] or 0)
    out = []
    for msa, m in by.items():
        total = m.get("Overall") or 0
        if total:
            out.append({"metro": msa, "businesses": int(total),
                        "hispanic_owned": round(m.get("Hispanic", 0) / total, 3),
                        "women_owned": round(m.get("Female", 0) / total, 3),
                        "veteran_owned": round(m.get("Veteran", 0) / total, 3)})
    return sorted(out, key=lambda r: -r["hispanic_owned"])


def graduates():
    """Graduates by program: San Antonio, and the average of its peers."""
    rows = sql(f'SELECT "MSA", "Program", "Graduates" FROM "{GRADUATES}"')
    home, peers = {}, {}
    for r in rows:
        n = float(r["Graduates"] or 0)
        if r["MSA"] == HOME:
            home[r["Program"]] = n
        else:
            peers.setdefault(r["Program"], []).append(n)
    return sorted(({"program": p, "san_antonio": int(n), "peer_average": round(sum(peers.get(p, [0])) / max(1, len(peers.get(p, []))))}
                   for p, n in home.items()), key=lambda r: -r["san_antonio"])


def b(n):
    return f"${n / 1e9:,.1f}B"


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--owners", action="store_true", help="who owns the businesses, by metro")
    ap.add_argument("--graduates", action="store_true", help="graduates by program, against the peers")
    ap.add_argument("--json", action="store_true", help="print JSON instead of tables")
    args = ap.parse_args()

    if args.owners:
        result = {"owners": owners()}
    elif args.graduates:
        result = {"graduates": graduates()}
    else:
        result = {"growth": growth(), "industries": industries()}
    result["credit"] = CREDIT
    if args.json:
        print(json.dumps(result, indent=2))
        raise SystemExit

    if args.owners:
        print("Share of businesses by owner, among each metro's businesses with owner data:\n")
        print(f"  {'':<14}{'Hispanic':>10}{'Women':>8}{'Veterans':>10}")
        for r in result["owners"]:
            mark = "→ " if r["metro"] == HOME else "  "
            print(f"{mark}{r['metro']:<14}{r['hispanic_owned']:>10.0%}{r['women_owned']:>8.0%}{r['veteran_owned']:>10.0%}")
    elif args.graduates:
        print("Graduates by program, San Antonio against the average of its seven peers:\n")
        for r in result["graduates"]:
            print(f"  {r['san_antonio']:>7,}  vs {r['peer_average']:>7,}  {r['program']}")
    else:
        g = result["growth"]
        print(f"GDP growth, {g[0]['from']}–{g[0]['to']}, San Antonio and its peers:\n")
        for i, r in enumerate(g, 1):
            mark = "→ " if r["metro"] == HOME else "  "
            print(f"{mark}{i}. {r['metro']:<14}{r['growth']:>6.0%}   {b(r['gdp_from'])} → {b(r['gdp_to'])}")
        ind = result["industries"]
        print(f"\nSan Antonio's target industries, {ind[0]['year'] if ind else ''} GDP:")
        for r in ind:
            grew = f"  {r['growth']:+.0%} since {r['growth_since']}" if r["growth"] is not None else ""
            print(f"  {b(r['gdp']):>8}  {r['industry']}{grew}")
    print(f"\n{CREDIT}")
