# Funded projects

The Alamo Area Metropolitan Planning Organization decides which road and transit projects across Bexar, Comal, Guadalupe and part of Kendall counties get federal and state money. Its **Transportation Improvement Program for 2027–2030** lists 68 funded projects with cost, year and agency. Its resilience study scores **6,372 road segments** for how much of each floods. This asks both, and lets the server do the adding up.

```sh
python3 main.py                  # totals by year and agency, then the ten biggest
python3 main.py --county Bexar
python3 main.py --flooding       # streets with the most road under a 100-year river flood
python3 main.py --json
```

```
Funded projects, 2027–2030

  2027   31 projects   $1,030.0M
  2028   18 projects     $842.9M
  ...
The biggest:
    $347.1M  2028  IH 35, FM 3009 to Guadalupe Comal County Line (Guadalupe) · TxDOT
```

## About the data

- **TIP_2027_2030** has each project's road, public description, total cost, fiscal year, agency, county and limits (from, to). Cancelled projects are left out.
- **Roads_Exposure_Risk** gives each segment the percent of it exposed to river (fluvial) and rain (pluvial) flooding in 5- to 500-year storms. Lengths are in US survey feet (the layer is in Texas South Central State Plane). It is a model of exposure, not a forecast.

## Where to take it

- **Where the money goes.** The City's 370 bond projects (`peek` finds `BondProject`) beside these 68, on one map.
- **Money meets water.** Which funded projects run along the most flood-exposed roads?
- **Your commute.** Draw your route and list the segments with the highest 100-year exposure.

## Source

Alamo Area MPO feature services under `services1.arcgis.com/ZmHtsY5M3DRYt09u`: `TIP_2027_2030` and `Roads_Exposure_Risk`. Browse more at [AAMPO GeoNexus](https://aampo-openmap-nexus-mpo.hub.arcgis.com). No keys.

Data: Alamo Area Metropolitan Planning Organization
