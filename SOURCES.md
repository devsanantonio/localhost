# The sources

Three public agencies publish San Antonio's open data, and they publish different things because they do different jobs. This page explains what each one has, what only it has, and how to get at it.

**The short version:**

- **City of San Antonio** publishes what the city *does*: the services it delivers (311, permits, fire calls), the rules it sets (zoning, historic districts, overlays), the things it builds and maintains (streets, sidewalks, drainage), and its economy. It covers **city limits**.
- **Bexar County** publishes the *ground and the civic map*: census geography with population, schools, every district people vote in, and San Antonio as it was in 1896–97. It covers **the whole county**, suburbs and unincorporated areas included.
- **VIA Metropolitan Transit** publishes **the buses**: every route, stop and scheduled trip, and live positions.

The best projects usually combine them: the City's 311 calls divided by the County's census population, or the County's 1896 buildings beside the City's historic landmarks.

Counts and details below were checked in October 2026. Portals change, so treat numbers as approximate and check the source before you publish.

---

## City of San Antonio

**Portal:** [data.sanantonio.gov](https://data.sanantonio.gov) · about 166 datasets · **License:** CC BY 4.0 · **Credit:** `Data: City of San Antonio Open Data, CC BY 4.0`

### What's in it

| Area | Datasets | Good for |
|---|---|---|
| **Service requests** | 311 service calls, about 500,000 since 2020, with type, department, opened and closed times, service deadline, late or on time, council district, and location | The richest everyday data in either portal |
| **Building and growth** | Building permits, Board of Adjustment cases and variances, plats, plan reviews, annexation areas | Where the city is being built, block by block |
| **Planning rules** | Zoning, future land use, sector and corridor plans, historic districts and landmark sites, the River Improvement Overlay, the Alamo Viewshed, Mission Protection and World Heritage buffers, military overlay zones | Why the city looks the way it does: what can be built where, and what's protected |
| **Streets and infrastructure** | Streets, sidewalks, crosswalks, bike facilities, speed humps, traffic signs, storm drains and channels, low-water crossings, pavement condition, bond projects | Walking, biking and flooding projects |
| **Street safety** | Vision Zero projects, severe pedestrian and bicyclist injury areas | Safer streets, which is not the same as crime data |
| **Neighborhoods and boundaries** | Council districts (2022), neighborhood associations, neighborhood conservation districts, the Central Business District, Downtown District land use, TIRZ, opportunity zones | Boundaries to scope a project to one part of town |
| **Economy** | Businesses by ZIP and industry, industry clusters, employment and occupations, GDP and graduates against peer cities, economic development incentives | San Antonio's economy over time |
| **Fire** | Fire department calls for service, inspections, arson investigations | Emergency services inside city limits |
| **Parks and places** | Park boundaries, trails and trailheads, libraries, City Hall, public safety facilities | Where things are |
| **Health** | COVID-19 cases, deaths and vaccinations, by ZIP (countywide) | Historical public health |
| **New and unusual** | A pilot street-light sensor dataset, good-neighbor engagement events | Worth opening to see what's inside |
| **Police** | SAPD arrests, offenses, and calls for service | See "Build with care" in the README: the starters here don't use these |

### Only the City has

311, building permits, zoning and planning rules, fire department data, street infrastructure, street-safety data, the economy datasets, and the City's own neighborhood and council boundaries.

### How to get at it

The portal runs [CKAN](https://docs.ckan.org/en/latest/api/), and many of its geographic datasets are also ArcGIS feature services.

```sh
# Find datasets
https://data.sanantonio.gov/api/3/action/package_search?q=311

# Read rows from a dataset's table (resource_id from the dataset page)
https://data.sanantonio.gov/api/3/action/datastore_search?resource_id=...&limit=100

# Ask questions in SQL, so you don't download everything
https://data.sanantonio.gov/api/3/action/datastore_search_sql?sql=SELECT "COUNCIL_DIST", COUNT(*) FROM "resource-id" GROUP BY "COUNCIL_DIST"
```

**Watch for duplicate copies.** Some datasets exist twice: once as a CKAN table and once as an ArcGIS layer, with different column names. 311 calls are `COUNCIL_DIST` and `TYPENAME` in the CKAN table, and `CouncilDistrict` and `TypeName` in the ArcGIS layer the `311-by-district` starter uses. Pick one copy and stay with it.

**Filter on the server.** CKAN supports `filters` and full SQL, and ArcGIS supports `where` and `outStatistics`. Downloading everything and filtering locally is slower, and it hides the fact that the API could have done it.

---

## Bexar County

**Portal:** [gis-bexar.opendata.arcgis.com](https://gis-bexar.opendata.arcgis.com) · 35 items, 27 of them map layers · **License:** set per dataset, in each layer's description · **Credit:** `Data: Bexar County Information Technology GIS`

### What's in it

| Area | Datasets | Good for |
|---|---|---|
| **San Antonio, 1896–97** | **Historic Buildings (1896):** 15,349 building outlines from the Sanborn fire-insurance maps, with building type, land use, owner, **number of floors** and square footage. **City Blocks (1896).** **Historic Points of Interest (1896–97):** about 4,200 places. **Residences** and **Employment (1897):** about 21,000 and 11,000 records from the city directory | History no other county has. The floor counts mean the 1896 city can be rebuilt in 3D |
| **Census geography** | Census tracts, block groups and blocks, with **2020 Census population and race counts** (`P1_001N` is total population), and a data dictionary | Anything per person: divide by population before comparing areas |
| **Who represents you** | Voter precincts, early voting sites, U.S. Congress (redistricted for 2026), Texas House, Texas Senate and State Board of Education (redistricted 2022), County Commissioner precincts | "Who represents me?" projects |
| **Courts** | Justice of the Peace and Constable precincts and offices | County justice geography |
| **Schools** | Public and private schools | Not in the City's portal |
| **Emergency services** | Emergency Services District (ESD) legal boundaries and response areas | Who answers 911 outside city limits |
| **Places** | County parks, libraries, military installations, ZIP code areas, the county boundary | Countywide reference |
| **Pointers, not data** | Address points and streets, parcels, plat maps and land records, contours, traffic lights and signs, foreclosure notices | These are PDFs explaining where to request the data from other County offices |

### Only the County has

The 1896–97 history, census geography with population, schools, voting and representation districts, courts geography, emergency services districts, and countywide coverage beyond city limits.

### Use with care

- **The 1897 Residence and Employment layers are real people,** with names and occupations, and race recorded in the language of the time. Use them for history in aggregate, never to look up individuals.
- **Election data:** the early voting sites layer is a reference, not the official list. For where and when to vote, always link the Bexar County Elections Department and [VoteTexas.gov](https://www.votetexas.gov).

### How to get at it

Every layer is an ArcGIS feature or map service. Find a layer's service address on its page in the portal, then query it:

```sh
# Count, filter, and get GeoJSON in latitude and longitude
.../FeatureServer/0/query?where=1=1&outFields=*&outSR=4326&f=geojson

# Which polygon is this point in? (e.g. which voter precinct is Geekdom in)
.../MapServer/0/query?geometry=-98.4936,29.4241&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=*&f=json
```

Services return at most 1,000 to 2,000 features per request: page with `resultOffset` until `exceededTransferLimit` is false. The `san-antonio-1897` starter shows how.

---

## VIA Metropolitan Transit

**Developer page:** [viainfo.net/developers-resources](https://www.viainfo.net/developers-resources/) · **License:** VIA's developer license · **Credit:** `Data provided by VIA Metropolitan Transit`

### What's in it

**The schedule (GTFS).** One zip, about 6 MB: `https://www.viainfo.net/BusService/google_transit.zip`. [GTFS](https://gtfs.org) is the format every transit agency and trip planner uses, so what you learn here works for any city. Inside:

| File | What it holds |
|---|---|
| `stops.txt` | About 6,100 stops, with names, coordinates and wheelchair boarding |
| `routes.txt` | 88 routes |
| `trips.txt` | About 14,700 scheduled trips, each with a route, direction and destination sign |
| `stop_times.txt` | When every trip reaches every stop (the big one, about 35 MB unzipped) |
| `calendar.txt`, `calendar_dates.txt` | Which days each schedule runs, and the holiday exceptions |
| `shapes.txt` | The line each route draws on a map |
| `transfers.txt`, `fare_attributes.txt`, `fare_rules.txt` | Transfers and fares |
| `agency.txt`, `feed_info.txt` | Who publishes it, and the dates the schedule is valid |

VIA publishes a new schedule a few times a year; `feed_info.txt` says which dates the current one covers.

**Live data (GTFS-realtime).** Four protobuf feeds:

| Feed | Address |
|---|---|
| Vehicle positions | `http://gtfs.viainfo.net/vehicle/vehiclepositions.pb` |
| Trip updates (live arrival predictions) | `http://gtfs.viainfo.net/tripupdate/tripupdates.pb` |
| Service alerts | `http://gtfs.viainfo.net/alert/alerts.pb` |
| Combined feed | `http://gtfs.viainfo.net/gtfs-realtime/trapezerealtimefeed.pb` |

They're served over plain `http://`, so a web page on `https://` can't fetch them directly: put a small server or serverless function in between. Read them with `gtfs-realtime-bindings` (Python or JavaScript).

### Only VIA has

The buses: every route, stop and trip, and where buses are right now. Neither portal carries transit.

### The license, in practice

- Use is limited to **"uses that utilize the VIA Data for assisting mass transportation riders."** A departure board or a "getting here" block qualifies; analysis unrelated to riders may not.
- Credit **"Data provided by VIA Metropolitan Transit"** wherever the data shows.
- **No VIA logos or trademarks,** and never present a project as VIA's, or as made with or in partnership with VIA.
- The data is as-is, VIA can change or stop it without notice, and using it means accepting VIA's indemnity terms.

The full summary of every source's terms is in [ATTRIBUTION.md](ATTRIBUTION.md).
