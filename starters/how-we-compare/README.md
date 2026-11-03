# How we compare

Not every question about San Antonio is about a place. The City's Economic Development Department publishes San Antonio beside seven peer metros (Austin, Charlotte, Dallas, Houston, Jacksonville, Phoenix and San Diego): how fast each economy grew, how much comes from the industries San Antonio is betting on, who owns the businesses, and what the colleges graduate. This asks the City's API in SQL and ranks them.

```sh
python3 main.py                 # GDP growth since 2020, and San Antonio's target industries
python3 main.py --owners        # Hispanic-, women- and veteran-owned shares of businesses
python3 main.py --graduates     # graduates by program, against the peer average
python3 main.py --json
```

```
GDP growth, 2020–2025, San Antonio and its peers:

  1. Austin           71%   $155.8B → $266.8B
  ...
→ 7. San Antonio      55%   $125.7B → $195.2B

Share of businesses by owner:
                  Hispanic   Women  Veterans
→ San Antonio          22%     24%        7%
  San Diego            13%     24%        5%
```

## About the data

Four tables from the City's portal, each a comparison the department chose: **GDP SATX and Peer** (overall and five target industry clusters: bioscience, IT security and infrastructure, mobility, corporate services, sustainable energy), **Firm Ownership** (businesses by owner gender, ethnicity, race, veteran status), and **Graduates SATX and Peers** (completions by program). They are metro areas (MSAs), not city limits. The industry clusters are published for one year so far.

The owner shares are counts of businesses with each kind of owner over all businesses with owner data, so they don't need to add to 100%.

## Where to take it

- **One chart, eight cities.** GDP by year for every metro, San Antonio highlighted.
- **The talent pipeline.** Graduates in computer science against the IT security cluster's GDP. Is San Antonio training for the industries it wants?
- **More tables like these.** The same department publishes occupations, median income, income and computer access, access to capital and peer-city business counts. `datastore_search_sql` works on all of them.

## Source

[data.sanantonio.gov](https://data.sanantonio.gov), City Government datasets, queried through `datastore_search_sql`. Resource ids are at the top of `main.py`. No keys.

Data: City of San Antonio Open Data, CC BY 4.0
