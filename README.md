<picture>
  <source media="(prefers-color-scheme: dark)" srcset="brand/localhost-210-lockup-dark.svg">
  <img alt="localhost:210 — build with San Antonio's open data, a DEVSA project" src="brand/localhost-210-lockup-light.svg" width="560">
</picture>

# localhost

**Every developer has a localhost. This one is San Antonio.**

```
guest@devsa ~ % curl localhost

  → 500,000+ 311 calls since 2020, by street, district and department
  → 6,098 VIA bus stops, 88 routes, every scheduled trip
  → 4,200 places from San Antonio in 1897, mapped over today's streets
  → 168 City datasets · 35 County map layers · no API keys
```

The City of San Antonio, Bexar County and VIA all publish their data in the open. Almost nobody builds with it, because it's scattered across three portals with three sets of rules and no obvious place to start. This is the place to start: what's out there, what it's good for, how to use it without breaking any rules, and a working program for each source that runs in under a minute.

No sign-up. No keys. Python and an internet connection.

```sh
git clone https://github.com/devsanantonio/localhost
cd localhost/starters/san-antonio-1897
python3 main.py && open map.html     # macOS; see the starter for Windows and Linux
```

## Pick a starter

| Starter | Source | Build from it |
|---|---|---|
| [**San Antonio, 1896–97**](starters/san-antonio-1897) | Bexar County | A map of the city about 130 years ago: saloons, wagon yards, breweries, schools, over today's streets. Data almost no other city has. |
| [**Next bus**](starters/via-next-bus) | VIA | Type a stop, get the next buses. The bones of a departure board, a bot, or the transit app you wish existed. |
| [**311 by district**](starters/311-by-district) | City of San Antonio | Half a million service calls, counted server-side in about two seconds. What each district calls about, and how often it closes late. |

Each one is a single Python file using only the standard library, short enough to read before you run it. Read it, break it, take it somewhere.

## What to build

Starters are the first commit, not the project. A few directions, any of which would be a strong portfolio piece or a Build-and-tell Friday post:

- **Then and now.** Pick a block downtown and put the 1897 businesses next to what's there today.
- **Walk sheds.** Which neighborhoods are more than a quarter mile from a bus that comes every 15 minutes?
- **Your district's dashboard.** 311 calls by type and month for one council district, updated nightly with a GitHub Action.
- **A departure board** for a library, a coworking space or a dorm lobby.
- **Something we haven't thought of.** The City alone has 168 datasets. Most have never been charted by anyone outside City Hall.

Using a coding agent? It's welcome here. [AGENTS.md](AGENTS.md) gives it the sources, the commands and the ground rules, so what it builds follows the same rules you would.

Maintained by [DEVSA](https://www.devsa.community), the nonprofit that connects the people building San Antonio tech. DEVSA isn't affiliated with the City, the County or VIA, and nothing here speaks for them. The data is theirs. This is the way in.

## The sources

**New here? Read [SOURCES.md](SOURCES.md)** for the full guide: what each agency publishes, what only it has, the field names, and how to query each API.

### City of San Antonio — [data.sanantonio.gov](https://data.sanantonio.gov)

About 170 datasets across 311 service requests, building permits, parks and trails, transportation, culture and events, city finances and more.

- **License:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Use it for anything, including commercial work, with credit to the City of San Antonio.
- **How to get it:** every dataset has CSV downloads. The portal also has a [CKAN API](https://data.sanantonio.gov/api/3/action/package_list) for finding datasets, and many geographic ones are live ArcGIS feature services you can query directly (that's what `311-by-district` does).
- **Good places to start:** 311 Service Calls, Building Permits, Parks and Trails.

### Bexar County — [gis-bexar.opendata.arcgis.com](https://gis-bexar.opendata.arcgis.com)

About 35 geographic layers: county and precinct boundaries, ZIP code areas, census tracts and block groups, schools, libraries, parks, voting sites, military installations — and a set of **historic layers from 1896–97** that almost no other county has: city blocks from Sanborn fire insurance maps, and the people, workplaces and points of interest of the 1897 city directory.

- **License:** no single license on the portal. Each dataset carries its own terms in its description, usually a disclaimer that the data is for display and reference. The historic layers ask: *"When used please credit: Bexar County Information Technology GIS."* Read the description of any layer before you publish with it.
- **How to get it:** every layer is an ArcGIS feature or map service with a query API that returns JSON or GeoJSON. Six catalog entries (parcels, plats, contours and others) are PDFs pointing to other County offices, not data.

### VIA Metropolitan Transit — [viainfo.net/developers-resources](https://www.viainfo.net/developers-resources/)

VIA's full schedule as [GTFS](https://gtfs.org) (routes, stops, trips, stop times and shapes), plus realtime feeds for vehicle positions, trip updates and service alerts as GTFS-realtime.

- **License:** VIA's own developer license. Read it in full before you build. The parts that shape what you can make:
  - Use is limited to **"uses that utilize the VIA Data for assisting mass transportation riders."**
  - Credit VIA as **"Data provided by VIA Metropolitan Transit"** (or "Data provided by VIA").
  - **Do not use VIA's logos or trademarks**, and don't present yourself as VIA, its agent or its partner.
  - The data is provided as is, and by using it you agree to VIA's indemnity terms.
- **How to get it:** the schedule is a zip at `https://www.viainfo.net/BusService/google_transit.zip`. The realtime feeds are served over plain `http://`, so a browser app on an `https://` page can't fetch them directly. Put a small server or serverless function in between.

The full rules, with the exact credit lines to copy, are in [ATTRIBUTION.md](ATTRIBUTION.md).

## Build with care

Some of this data is about people. A few lines we hold to, and ask contributors to hold to as well:

- **No rankings of neighborhoods by crime.** The City publishes police calls, offenses and arrests. They're public, and there's real work to be done with them, but a "most dangerous neighborhoods" map built from raw counts tells a story about San Antonio that the data doesn't support. Starters here won't use them.
- **The 1897 directory is about real people.** It records names, jobs and, in the language of the time, race. Treat it as history — what the city was, who built it — not as a lookup of individuals.
- **Credit every source, every time.** It's the license, and it's how the people who publish this data find out it's being used.

## Show us what you built

Built something with San Antonio data? Add it to [SHOWCASE.md](SHOWCASE.md) with a pull request: one line, a link to your repo or demo, and which sources it uses. Then share it in **#build-and-tell** on the [DEVSA Discord](https://www.devsa.community/discord) on a Friday.

Found a broken link, a stale dataset or a field that doesn't mean what its name says? [Open an issue](https://github.com/devsanantonio/localhost/issues). We collect these, and they're the most useful thing we can pass back to the people who publish the data.

## Contributing

New starters, better explanations of a dataset, and fixes are all welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

The code in this repo is [MIT](LICENSE). The data belongs to its publishers and is used under their terms. See [ATTRIBUTION.md](ATTRIBUTION.md).
