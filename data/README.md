# data/

Written every Monday by the [weekly check](../.github/workflows/weekly.yml). Don't edit by hand.

- **`catalog.json`**: every public layer from every publisher (ArcGIS layers from `peek --all`, plus VIA's feeds, the USGS gauges and the J-17 well), with title, publisher, address, last-modified date and credit line.
- **`changes.json`**: layers their publisher updated in the last 14 days, newest first; `change` is `new` for layers that weren't in the previous catalog.
- **`status.json`**: whether each starter ran against its live source, and so whether each publisher answered.

[devsa.community/localhost](https://www.devsa.community/localhost) reads these to show the catalog, what's new, and which sources answered this week.
