# Who represents me

Every address in San Antonio sits inside ten districts at once: City Council, County commissioner, justice of the peace, constable, the Texas House and Senate, the State Board of Education, Congress, a school district and a voter precinct. Bexar County maps all of them except City Council, which the City maps. This asks each map which district a point falls in, and adds how many people lived in that block group in the 2020 Census.

```sh
python3 main.py                                            # Geekdom, Houston and Soledad
python3 main.py --address "100 Military Plaza, San Antonio, TX"
python3 main.py --near 29.6500,-98.6500                    # outside the city limits
python3 main.py --json
```

```
Who represents 29.42637, -98.49337:

  City Council              District 1
  County Commissioner       Precinct 4 · map lists Tommy Calvert Jr.
  Justice of the Peace      Precinct 4 · map lists Michele Garcia
  Constable                 Precinct 4 · map lists Kathryn Brown
  Texas House               District 123 · map lists Diego Bernal
  Texas Senate              District 26 · map lists José Menéndez
  State Board of Education  District 3
  U.S. House                Texas District 20
  School district           San Antonio ISD
  Voter precinct            4001

  Census block group 480291101002: 1,076 people in 2020
```

`--address` uses the [U.S. Census Bureau's geocoder](https://geocoding.geo.census.gov), which is free and needs no key. Ten map queries run at once, so an answer takes a few seconds.

## Districts are data; names are a convenience

The district lines come from the County's redistricting layers, and those are what this starter is sure of. The officeholders' names are typed into the same maps by hand, and they lag: in November 2026, one of them still listed a state representative who left office in 2023. So names print as what **the map lists**, never as fact, and the JSON calls the field `map_lists`. Check a name before you rely on it, and if you find a stale one, [open an issue](https://github.com/devsanantonio/localhost/issues). That's exactly the kind of fix worth passing back to the County.

## Build with care

Keep it about places, not people's choices. A district lookup is civic infrastructure; don't pair it with voter files, party data or anything that profiles how a neighborhood votes. Districts change with redistricting, so date anything you publish.

## Where to take it

- **A "your ballot" page.** Look up an address, then link each district to its race on the County's sample ballot.
- **Per-person numbers.** The block group's 2020 population is the denominator for anything per resident: 311 calls ([`311-by-district`](../311-by-district)), permits, bus service ([`housing-near-you --bus`](../housing-near-you)).
- **District fact sheets.** Pick a council district and gather what every publisher says about it.
- **Name checker.** Compare the names on the County's maps against the Texas Legislature's and the County's own sites, and file what's out of date.

Data: Bexar County Information Technology GIS (redistricting, precinct, school-district and 2020 Census block-group layers); City of San Antonio Open Data, CC BY 4.0 (council districts). Address lookup: U.S. Census Bureau. See [ATTRIBUTION.md](../../ATTRIBUTION.md).
