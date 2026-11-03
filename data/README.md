# data/

Written every Monday by the [weekly check](../.github/workflows/weekly.yml). Don't edit by hand.

- **`catalog.json`**: every public dataset from every publisher, with title, publisher, kind, address, last-modified date and credit line. `kind` is `Map layer` (ArcGIS layers, from `peek --all`), `Table` (the City's CKAN tables), `Live feed` (VIA's realtime feeds, the USGS gauges) or `Download` (VIA's schedule zip, the J-17 well). `count`, `by_publisher` and `by_kind` total them.
- **`changes.json`**: datasets their publisher updated in the last 14 days, newest first; `change` is `new` for datasets that weren't in the previous catalog.
- **`status.json`**: whether each starter ran against its live source, and so whether each publisher answered.

These are the current counts. The numbers in [SOURCES.md](../SOURCES.md) are what each portal's own listing showed when it was written, and run lower: the agencies' ArcGIS accounts publish far more than their portals list.
