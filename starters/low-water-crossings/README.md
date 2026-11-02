# Low water crossings

Where a road dips through a creek bed, a few inches of moving water can float a car. Opportunity Home San Antonio, the city's housing authority, publishes a map of the **156 low water crossings** inside the FEMA floodplain in Bexar County. This lists the ones nearest a point and writes `map.html` with every crossing on it.

> **This is not a flood warning.** It shows where crossings are, not whether they are under water. For closures and warnings, use [BexarFlood.org](https://www.bexarflood.org) and the [National Weather Service](https://www.weather.gov/ewx/). Turn around, don't drown.

```sh
python3 main.py                                  # nearest Geekdom, Houston and Soledad
python3 main.py --near 29.5150,-98.5320 --count 5
python3 main.py --json
open map.html
```

```
The 8 low water crossings nearest 29.42637, -98.49337 (of 156 in Bexar County):

    2.3 mi  E Mulberry at San Antonio River
    2.4 mi  Woodlawn at Martinez Creek
    2.8 mi  Hildebrand at Kendall
```

## About the data

Each crossing is a point with a name ("Woodlawn at Martinez Creek") and an ID. The layer credits its points to the City of San Antonio's Transportation & Capital Improvements department and GIS. The City publishes its own copy too (`peek --find "low water"`).

## Where to take it

- **Your route.** Which crossings sit on the way you drive to work or school?
- **With the creek gauges.** `creek-levels` shows which creeks are rising; put the two on one map. Still not a warning.
- **With housing.** The same Opportunity Home service has its developments (layer 3). Which communities are near crossings?

## Source

Opportunity Home's `Opportunity_Home___Low_Water_Crossings_WFL1` feature service, layer 1, under `services2.arcgis.com/nH68joXCaOE0Iiws`. No keys.

Data: Opportunity Home San Antonio
