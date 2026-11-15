# Busiest roads

The Texas Department of Transportation counts traffic at fixed stations on state roads and publishes the **Annual Average Daily Traffic (AADT)** at each: how many vehicles pass on an average day, with up to twenty years of history. In Bexar County that's **893 stations**, counted through **2025**. TxDOT also publishes every construction project it runs: **428 active in Bexar, about $11.7 billion** of estimated construction, from planning to under way. This starter asks both, for any Texas county.

> **TxDOT's terms are stricter than the other publishers'.** Its data is for informational use only, with no warranty; it may not be used commercially or resold; and distributing it to third parties needs TxDOT's written consent. Run this to explore for yourself. Don't publish its output (a map, a chart, a screenshot, a table) or build a product on it without asking TxDOT first. See [ATTRIBUTION.md](../../ATTRIBUTION.md#texas-department-of-transportation).

## Run it

```sh
python3 main.py                              # the busiest count stations in Bexar County
python3 main.py --grew                       # where traffic grew most since 2019
python3 main.py --near 29.4241,-98.4936      # stations within 1,600 m of a point, and their trend
python3 main.py --building                   # TxDOT's active projects: by stage, then the biggest
python3 main.py --county Travis              # any Texas county
python3 main.py --json                       # any of the above as JSON
```

```
The busiest TxDOT count stations, Bexar County (2025):

   250,759 a day  I-410            29.49058, -98.56015  15H41008
   250,077 a day  I-410            29.50906, -98.54184  15H41009
   244,904 a day  I-410            29.51983, -98.51893  15H41010
   ...
```

`--grew` compares each station's latest year with 2019, before the pandemic dip, among stations that carried at least 10,000 vehicles a day then. `--near` asks the service for every station inside the radius; TxDOT counts state roads, so a point on a city street may find none.

## Where to take it

- **Did transit follow?** Put the stations that grew most beside VIA's routes (`via-next-bus`, or VIA's GTFS) and ask where traffic grew and service didn't.
- **Building where it floods.** Match `--building`'s active projects against the Alamo Area MPO's flood-exposed roads (`funded-projects --flooding`) and its funded projects.
- **Your commute.** `--near` on a few points of your own route, and how each changed since 2015.

Keep what you make for yourself unless TxDOT has said yes; see the note above.

## The source

Texas Department of Transportation feature services under `services.arcgis.com/KTcxiTD9dsQw4r7Z`:

- `TxDOT_AADT_Annuals_(Public_View)`: one point per count station, the latest AADT and nineteen years back, the road (`ON_ROAD`, written like `IH0410`), county and district.
- `TxDOT_DCIS_All_Projects`: every project, with its control-section-job number, highway, limits, type of work, stage (`PROJ_STG`), status (`PROJ_STAT`) and estimated construction cost (`EST_CONSTRUCTION_COST`; the similar `EST_CONST_COST` is empty).

TxDOT's own portal is at [gis-txdot.opendata.arcgis.com](https://gis-txdot.opendata.arcgis.com). Questions about the counts go to TPP-Traffic-Data@txdot.gov.

```
Data: Texas Department of Transportation
```

For informational use only, with no warranty. Not for commercial use or resale; distribution to third parties needs TxDOT's written consent.
