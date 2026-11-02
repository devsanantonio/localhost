---
name: localhost
description: San Antonio's open data from seven publishers (City of San Antonio, Bexar County, VIA, San Antonio River Authority, Alamo Area MPO, Opportunity Home, Edwards Aquifer Authority, plus USGS gauges). Use when building with or answering questions about this data, adding or changing a starter, or finding which publisher has a dataset.
---

# Building with San Antonio's open data

Read [AGENTS.md](../../../AGENTS.md) first. Its rules are not style preferences: two are license terms (credit lines, VIA's license) and the rest are this repo's standards (no affiliation claims, no neighborhood crime rankings, no survey layers, the 1897 people layers in aggregate only, the flood starters are not warnings). If a request would break one, say which and offer an alternative.

## Find the data before writing code

- `python3 starters/peek/main.py --find <word> --json` searches every publisher's public layers.
- `python3 starters/peek/main.py <layer address> --json` shows its fields, row count, last change, sample rows and credit line.
- `data/catalog.json` lists every public layer, refreshed weekly. `SOURCES.md` explains what each publisher has and how to query it.

## Get answers from the starters

Every starter takes `--json` and prints one JSON object with its credit line. Prefer running a starter over re-implementing its query:

| Question | Starter |
|---|---|
| 311 calls by district or category | `311-by-district` |
| Building permits near a point | `permits-near-you` |
| Next scheduled buses at a stop | `via-next-bus` |
| Acequias, 1718 onward | `acequias` |
| San Antonio in 1896–97 | `san-antonio-1897` |
| Creek and river levels now; draft floodplains | `creek-levels` |
| The aquifer level, drought trigger, springflow | `aquifer-today` |
| Funded road and transit projects; flood-exposed streets | `funded-projects` |
| Low water crossings near a point | `low-water-crossings` |

## When you add or change a starter

One folder, `main.py` and `README.md`, Python 3.9+, standard library only, no keys. Ask the API to do the work (`where`, `outStatistics`, `outSR=4326`), page past 1,000 to 2,000 features, add `--json`, print the credit line, run it against the live source and say what it printed, add it to the README table, and add a smoke case to `scripts/check.py`.
