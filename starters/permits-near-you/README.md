# Permits near you

Before anyone builds, remodels or rewires in San Antonio, the City issues a permit, and it publishes every one. Give this a point and it asks the City what's been permitted around it since January 2025: the work, the declared value, and how long the permit took to come through.

```sh
python3 main.py                                          # around Geekdom, Houston and Soledad
python3 main.py --near 29.421628,-98.476653 --meters 60  # Central at Commerce
python3 main.py --since 2026-01-01
```

```
13 building permits within 60 m of 29.42163, -98.47665, issued since 2025-01-01:

  2026-03-16  Comm New Building  $52,000,000  · 1231 E Commerce St  · Central at Commerce  · issued in 139 days
  2026-08-04  Comm Swimming Pool  $300,000  · 1231 E Commerce St  · Central at Commerce  · issued in 25 days
  2026-03-03  Electrical General  · 1200 block of E Commerce St  · issued in 157 days
```

The City's portal runs on CKAN, which takes plain Postgres SQL at `datastore_search_sql`. The script builds one `SELECT` with a box around your point and sends it; the City's database does the filtering. Print the query (`sql()` returns it) and paste it after `?sql=` in a browser to see the raw JSON.

## About the data

Each permit has its type, work type, project name, address, coordinates, the dates it was filed and issued, the declared value and the square footage. Declared value is filled in mostly on large commercial work, so most trade permits show none.

Every permit also names a **primary contact**, and on a house that is usually the homeowner. This script never asks for that field. It shows commercial permits by address and project name, and anything else by its block (`1200 block of E Commerce St`), since it may be someone's home. Keep that rule in whatever you build from it.

Signs, banners, billboards, garage sales and tree affidavits are left out: they aren't building.

## Where to take it

- **Watch it happen.** Group by month and draw each permit as a dot the day it was issued. [Watch downtown get built](https://www.devsa.community/localhost#city), on DEVSA's site, does this for downtown.
- **The wait.** Median days from filing to permit, by permit type or council district (the `CD` field). Which kinds of work wait longest?
- **Go back to 2020.** The same dataset has a `PERMITS ISSUED 2020-2024` resource (`c22b1ef2-dcf8-4d77-be1a-ee3638092aab`). Its dates are timestamps, and its coordinates are in Texas State Plane South Central, in feet, not latitude and longitude: converting them is a good first exercise.

## Source

[Building Permits](https://data.sanantonio.gov/dataset/building-permits), resource `PERMITS ISSUED` (`c21106f9-3ef5-4f3a-8604-f992b4db7512`), queried through `data.sanantonio.gov/api/3/action/datastore_search_sql`.

Data: City of San Antonio Open Data, CC BY 4.0
