# VIA next bus

Type part of a bus stop's name; get the next departures from it, from VIA's published schedule.

```sh
python3 main.py "houston & st mary"
python3 main.py "medical & babcock" --count 15
```

The first run downloads VIA's schedule, a 6 MB [GTFS](https://gtfs.org) zip, and keeps it beside the script. GTFS is the format every transit agency publishes and every trip planner reads, so what you learn here works for any city.

It reads five files from the zip: `stops.txt` (where), `stop_times.txt` (when each trip reaches each stop), `trips.txt` and `routes.txt` (which bus), and `calendar.txt` with `calendar_dates.txt` (which days a schedule runs, including holidays).

## Where to take it

- **Realtime.** VIA publishes live vehicle positions, trip updates and alerts as [GTFS-realtime](https://gtfs.org/realtime/), a protobuf format: `pip install gtfs-realtime-bindings` reads it. The feeds are served over plain `http://`, so a web app on `https://` needs a small proxy in between: a serverless function works.
- **A map.** `shapes.txt` is every route's line. Draw them with Leaflet or MapLibre.
- **Walk sheds.** Which neighborhoods are more than a quarter mile from a stop with frequent service? Combine stops with the County's census block groups.
- **A departure board** for a lobby, a library or a coworking space.

## VIA's terms, briefly

VIA's data is licensed for uses that help transit riders, and that's what this starter is. Credit VIA as *"Data provided by VIA Metropolitan Transit"*. Don't use VIA's logos or trademarks, and don't present your project as VIA's or as a partnership with VIA. Full summary in [ATTRIBUTION.md](../../ATTRIBUTION.md); the license itself is on [VIA's developer page](https://www.viainfo.net/developers-resources/).

Data provided by VIA Metropolitan Transit
