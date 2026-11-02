# Creek levels

The U.S. Geological Survey measures the water in San Antonio's river and creeks every 15 minutes: how high it stands at each gauge, and how much is flowing. This prints the latest reading at the two gauges downtown and how each has moved over the last day. Give it a point and it also says whether that point sits inside the San Antonio River Authority's draft floodplain maps.

> **This is not a flood warning.** Gauges lag, and a creek can rise in minutes. For warnings and road closures, use the [National Weather Service](https://www.weather.gov/ewx/) and [BexarFlood.org](https://www.bexarflood.org). Turn around, don't drown.

```sh
python3 main.py                                   # the San Antonio River and San Pedro Creek, downtown
python3 main.py --site 08178000 --site 08178800   # any USGS gauge numbers
python3 main.py --near 29.3270,-98.4500           # is this point in a draft floodplain?
python3 main.py --json
```

```
San Antonio Rv at San Antonio, TX (USGS 08178000) · 2026-11-02 16:00
  water height      4.00 ft   +0.01 ft in 24 h
  flow              27.9 cfs  +0.4 cfs in 24 h
San Pedro Ck at Furnish St, San Antonio, TX (USGS 08178500) · 2026-11-02 16:00
  water height      2.75 ft   +0.17 ft in 24 h
  flow              32.8 cfs  +23.1 cfs in 24 h
```

## About the data

- **USGS gauges** report gage height in feet (`00065`) and discharge in cubic feet per second (`00060`). "Gage height" is the water's height at the gauge against its own datum, not depth. A rise in a few hours matters more than the number itself.
- **The River Authority's floodplains** are its **draft** maps from 2022/23 studies, one layer per watershed. They are proposals, not the effective FEMA maps that decide insurance. Outside every zone is not a promise a place can't flood.

## Where to take it

- **When it rains.** Put these gauges beside the Alamo Area MPO's flood-exposed roads (`funded-projects --flooding`) and the low water crossings (`low-water-crossings`).
- **A rise chart.** `period=P7D` returns a week of 15-minute readings. Draw both creeks on one chart.
- **More gauges.** Search waterdata.usgs.gov for "San Antonio, TX". Salado, Leon and Olmos creeks all have them.

## Source

USGS Instantaneous Values service (`waterservices.usgs.gov/nwis/iv/`), and the River Authority's [Draft Floodplain](https://sariverauthority-sara-tx.opendata.arcgis.com) feature service. No keys.

Data: U.S. Geological Survey
This uses River Authority's data but is not endorsed or verified by River Authority. Retrieved <the date you ran it>.
