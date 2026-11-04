# Housing near you

Opportunity Home San Antonio, the city's housing authority, publishes every community it owns or partners on: **135 of them, about 19,000 homes**, from public housing to affordable and mixed-income. For each one: who it's for (families, or seniors and people with disabilities), how many homes and bedrooms, the year it was built, the council and school district, and whether residents get free Wi-Fi. This lists the communities nearest a point, and can say how well each is served by the bus.

```sh
python3 main.py                                   # nearest Geekdom, Houston and Soledad
python3 main.py --near 29.4110,-98.5200 --count 5
python3 main.py --bus                             # adds VIA: buses within a quarter mile, 7-9 a.m.
python3 main.py --districts                       # communities and homes by council district
python3 main.py --json
```

```
The 2 Opportunity Home communities nearest 29.42637, -98.49337 (of 135):

  Villa Hermosa  (209 m)
    Public Housing for seniors and people with disabilities · 66 homes (41 studio, 20 1-bed, 5 2-bed) · built 1970
    council district 1 · San Antonio ISD · free Wi-Fi
    nearest stop: FLORES & PECAN, 57 m · within a quarter mile, 7-9 a.m.: 117 buses an hour on 31 routes
```

Run `--bus` near downtown and then somewhere on the northeast side, and the difference is the point: 117 buses an hour on 31 routes beside one community, 2 an hour on a single route beside another. For a household without a car, that's the difference between a job across town being reachable or not.

`--bus` uses VIA's schedule. If you've run [`via-next-bus`](../via-next-bus), it reuses the copy that starter downloaded; otherwise it fetches one (about 6 MB). It counts every stop within a quarter mile, not only the nearest, and a bus that stops at two of them counts once.

## The data, honestly

The layer has a few rough edges, and this starter fixes them out loud rather than quietly:

- One housing type is spelled two ways ("Mixed-income Housing" and "Mixed-income Houseing"). They're merged.
- Three communities have council district `0`. They're outside the city limits, so they have no council district, and are listed that way.
- One record has no name or location. It's skipped.

Found another? [Open an issue](https://github.com/devsanantonio/localhost/issues). Small fixes like these are the most useful thing to pass back to the agency.

## Build with care

These are people's homes. List communities, count homes, map bus service, but don't pair this layer with crime or police data to rank places, and don't publish anything that singles out residents. The layer has the property office's phone and email; this starter doesn't use them.

## Where to take it

- **Walk sheds.** Run `--bus` for all 135 and map which communities have frequent service and which don't. ([issue #5](https://github.com/devsanantonio/localhost/issues/5) is the same question citywide.)
- **Seniors and the bus.** 45 communities are for seniors and people with disabilities. Which are farthest from a bus that comes every 15 minutes?
- **The Wi-Fi gap.** Free Wi-Fi is in place at some communities, in progress at others, and absent at the rest. Where, and how many homes?
- **By district.** `--districts` is the start of a council-district fact sheet; add the City's 311 calls from [`311-by-district`](../311-by-district).

Data: Opportunity Home San Antonio, informational use, per its disclaimer. Bus stops and schedule: Data provided by VIA Metropolitan Transit. See [ATTRIBUTION.md](../../ATTRIBUTION.md).
