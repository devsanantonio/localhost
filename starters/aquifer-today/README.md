# The aquifer today

Most of San Antonio's water comes out of the ground, from the Edwards Aquifer. The Edwards Aquifer Authority measures it every 15 minutes at the **J-17 index well** in Bexar County, and the U.S. Geological Survey measures what flows out at Comal and San Marcos Springs. This prints the latest J-17 level, its 10-day average, which J-17 drought trigger that average sits under, and the springflow.

```sh
python3 main.py
python3 main.py --days 30     # a longer average and range
python3 main.py --json
```

```
J-17 index well, Bexar County · Nov 2, 2026 2:00 AM CST (provisional)
  level           641.93 ft above sea level
  10-day average  639.02 ft   (range 637.29–642.76)
  by J-17 alone   Stage III: the 10-day average is below 640 ft
                  The authority also weighs springflow. Official stage: edwardsaquifer.org

Springflow, daily
  Comal Springs            156 cfs   2026-10-30
  San Marcos Springs        87 cfs   2026-11-01
```

## About the data

- **J-17** is reported as water level elevation in feet above sea level. The authority's CSV holds every reading since 1992, newest first. It is about 57 MB, so the script reads only the newest lines and stops.
- **Readings are provisional** (`P`) until the authority approves them.
- **Drought stages** for the San Antonio Pool start when J-17's 10-day average falls below 660 ft (Stage I), then 650, 640, 630 and 625 ft (Stage V). The authority also weighs springflow, so **the official stage can differ.** It is published at [edwardsaquifer.org](https://www.edwardsaquifer.org).
- **Springflow** is USGS's daily value, a day or two behind.

## Where to take it

- **A hundred years of water.** The full J-17 CSV goes back decades. Chart it, mark the droughts.
- **Rain to aquifer.** Put J-17 beside rainfall and see how long a wet week takes to show up.
- **A daily post.** Run it every morning with a GitHub Action and post the level to a channel.

## Source

The authority's J-17 download (`data.edwardsaquifer.org/GroundWater/DownloadGroundwaterCsv?siteId=J17WL&sensorName=WLE`) and the USGS Daily Values service (`waterservices.usgs.gov/nwis/dv/`, sites 08168710 and 08170000). No keys.

Data: Edwards Aquifer Authority
Data: U.S. Geological Survey
