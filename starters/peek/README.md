# Peek

Find a layer from any of San Antonio's publishers, then see what's in it, without knowing anything first.

```sh
python3 main.py --find flood
python3 main.py https://services1.arcgis.com/ZmHtsY5M3DRYt09u/arcgis/rest/services/Roads_Exposure_Risk/FeatureServer/0
```

`--find` searches the public layers of every publisher in [SOURCES.md](../../SOURCES.md) at once, newest first: the City, Bexar County, the San Antonio River Authority, the Alamo Area MPO, Opportunity Home San Antonio and the Edwards Aquifer Authority. Give it a layer's address (it ends in `/FeatureServer/0` or `/MapServer/0`) and it prints how many rows there are, when the layer last changed, every field and a few real rows, then the publisher's credit line.

It works because these agencies all publish the same way, as ArcGIS layers that answer the same queries. One script reads them all. Give it a service address without the layer number and it lists the layers inside.

## Try these

```sh
# Alamo Area MPO: 6,372 road segments, each with how much of it floods in a 5- to 500-year storm
python3 main.py https://services1.arcgis.com/ZmHtsY5M3DRYt09u/arcgis/rest/services/Roads_Exposure_Risk/FeatureServer/0

# City of San Antonio: 370 bond projects, with budget, spending, phase and council district
python3 main.py https://services.arcgis.com/g1fRTDLeMgspWrYp/arcgis/rest/services/BondProject/FeatureServer/0

# Alamo Area MPO: 68 funded road and transit projects for 2027–2030, with cost and year
python3 main.py https://services1.arcgis.com/ZmHtsY5M3DRYt09u/arcgis/rest/services/TIP_2027_2030/FeatureServer/0

# Bexar County: warming and cooling centers, County and City
python3 main.py https://maps.bexar.org/arcgis/rest/services/OEM/SeasonalShelters/MapServer/0
```

## Where to take it

- **Ask a real question.** Once you know the fields, the same `/query` endpoint takes `where` (SQL-ish filters), `outStatistics` (counts and sums done by the server) and `outSR=4326&f=geojson` (a map-ready file). `311-by-district` shows all three.
- **Put two publishers on one map.** The River Authority's watersheds under the MPO's flood-exposed roads; the City's bond projects beside the MPO's funded ones.
- **Check before you trust.** "Last changed" is there for a reason. Some layers haven't been touched in years.

## Care

Some public layers hold what people submitted through a form, such as surveys, feedback and applications, sometimes with names and addresses. `--find` leaves out the ones it can recognize by name, but it can miss one. If a layer holds anything about a person, don't republish it.

## Source

ArcGIS Online's search API (`arcgis.com/sharing/rest/search`) and each layer's own query endpoint. No keys.

The data belongs to each publisher. `peek` prints the right credit line for the layer you're looking at; the full list and each publisher's terms are in [ATTRIBUTION.md](../../ATTRIBUTION.md).
