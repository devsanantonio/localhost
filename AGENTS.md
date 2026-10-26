# AGENTS.md

Instructions for coding agents working in this repo. People are welcome to read it too.

## What this repo is

Starters and documentation for building with San Antonio's open data: the City of San Antonio, Bexar County, and VIA Metropolitan Transit. Each starter is one Python file under `starters/<name>/main.py` with a `README.md` beside it.

## Commands

```sh
python3 starters/311-by-district/main.py              # prints a table
python3 starters/311-by-district/main.py --district 5
python3 starters/via-next-bus/main.py "houston & st mary"
python3 starters/san-antonio-1897/main.py             # writes map.html and places-1897.geojson
python3 starters/acequias/main.py                     # prints nearby ditches; writes map.html and acequias.geojson
python3 starters/permits-near-you/main.py --meters 60
```

There is no build step and no test suite. A starter works if it runs against the live source and prints or writes what its README says.

## Conventions

- Python 3.9+, **standard library only**. No `requirements.txt`. If a starter truly needs a package (for example `gtfs-realtime-bindings` for VIA's realtime feeds), it goes in a separate starter whose README says so up front.
- One starter per folder: `main.py` and `README.md`. Generated files (`map.html`, `*.geojson`, `via_gtfs.zip`) are gitignored. Don't commit them.
- Prefer asking a source's API to do the work (ArcGIS `outStatistics`, `where`, `outSR=4326`) over downloading everything and filtering locally.
- ArcGIS feature services return at most 1,000 to 2,000 features per request. Page with `resultOffset` until `exceededTransferLimit` is false.
- No API keys exist for any of these sources. Never add one, and never commit credentials.

## Rules for anything that uses the data

These are not style preferences. Two are license terms, and the rest are this repo's standards.

1. **Credit every source** in the starter's README and in any output a person might share (a map, a chart, a page). Use the exact lines in [ATTRIBUTION.md](ATTRIBUTION.md):
   - `Data: City of San Antonio Open Data, CC BY 4.0`
   - `Data: Bexar County Information Technology GIS`
   - `Data provided by VIA Metropolitan Transit`
2. **VIA's license:** use is limited to helping transit riders. No VIA logos or trademarks, and never describe a project as VIA's, or as made with or in partnership with VIA.
3. **No affiliation claims.** Say "built on City of San Antonio open data", never "with the City" or "in partnership with" any of the three.
4. **No neighborhood crime rankings.** Don't build anything that ranks or scores areas from the SAPD datasets.
5. **The 1897 Residence and Employment layers record real people, with race.** Use them for history in aggregate, never as a lookup of individuals.

If a request would break one of these, say which one and suggest an alternative instead of building it.

## When you add or change a starter

- Run it against the live source before calling it done, and say what it printed.
- Update the starter table in the root `README.md`.
- Keep the README to: what it does, how to run it, where to take it, the source, and the credit line.
