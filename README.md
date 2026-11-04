<picture>
  <source media="(prefers-color-scheme: dark)" srcset="brand/localhost-210-lockup-dark.svg">
  <img alt="localhost:210 — build with San Antonio's open data, a DEVSA project" src="brand/localhost-210-lockup-light.svg" width="560">
</picture>

# localhost:210

**Seven APIs. No one place to find them. This is the place.**

localhost:210 turns San Antonio's open data into answers you can check.

```
guest@devsa ~ % curl localhost:210

  → the next real bus from any VIA stop, every scheduled trip
  → every building permit since 2025: what, where, how much, how long it took
  → San Antonio against its peer cities: growth, who owns the businesses
  → who represents any address, City Council to Congress
  → 135 housing communities, and how often a bus comes by
  → the river, the creeks and the aquifer, live
  → the acequias from 1718, and 4,200 places from 1897
  → 7 publishers · one catalog, rebuilt every Monday · no API keys
```

Seven public agencies publish San Antonio's data in the open: the City, Bexar County, VIA, the San Antonio River Authority, the Alamo Area MPO, Opportunity Home San Antonio and the Edwards Aquifer Authority. Each runs its own portal, with its own rules, and almost nobody builds with any of it, because there's no obvious place to start. This repo brings all seven together: what each one publishes, how to use it without breaking its rules, a list of every dataset they put out, and a small working program for each.

Three experiments built from it are at [devsa.community/localhost](https://www.devsa.community/localhost).

## How it works

Six steps take a dataset to an answer you can check. This repo does the first two for all seven agencies today. The rest is what we're building next, in the open.

| | Step | What happens | Where it lives |
|---|---|---|---|
| 1 | **Find** | Every dataset all seven publish, in one list, rebuilt every Monday by a GitHub Action | [`data/`](data) |
| 2 | **Fetch** | A small program for each agency, run against its live source every week, so a broken source opens an issue | [`starters/`](starters) |
| 3 | **Ask** | A question in plain English, to an AI agent that picks the right programs to answer it | [`starters/mcp`](starters/mcp) · *early* |
| 4 | **Run** | Any code the agent writes to answer, run in a sandbox, never on your machine | *next* |
| 5 | **Show** | The answer, with the code that made it and the agency it came from, so anyone can check it | *next* |
| 6 | **Return** | What you build goes in the [showcase](SHOWCASE.md); what's wrong with the data goes in an [issue](https://github.com/devsanantonio/localhost/issues), and on to the agencies | [`SHOWCASE.md`](SHOWCASE.md) |

**Where this is going:** anyone in San Antonio can ask their city's data a question, get an answer they can check, and the problems they find make it back to the people who publish it. Not an app: a habit, and the tools to make it easy.

## Start

No sign-up. No keys. Python 3.9+ and an internet connection.

```sh
git clone https://github.com/devsanantonio/localhost
cd localhost
python3 starters/via-next-bus/main.py "houston & st mary"     # the next buses from a stop near Geekdom
```

Then pick any starter below. Each one is a single Python file using only the standard library, short enough to read before you run it, and every one takes `--json`, so you can pipe its answer into your own code, a GitHub Action or an agent.

## The seven publishers

| Publisher | What only it has | Terms | Starters |
|---|---|---|---|
| **[City of San Antonio](https://data.sanantonio.gov)** | 311 calls, building permits, zoning, bond projects, the economy beside peer metros | CC BY 4.0 | [permits-near-you](starters/permits-near-you), [311-by-district](starters/311-by-district), [how-we-compare](starters/how-we-compare) |
| **[Bexar County](https://gis-bexar.opendata.arcgis.com)** | Every district people vote in, census population, schools, and the city in 1718 and 1896–97 | Per dataset, in each layer's description | [who-represents-me](starters/who-represents-me), [acequias](starters/acequias) |
| **[VIA Metropolitan Transit](https://www.viainfo.net/developers-resources/)** | Every route, stop and scheduled trip, and live bus positions | VIA's developer license: uses that help riders, no VIA logos | [via-next-bus](starters/via-next-bus) |
| **[San Antonio River Authority](https://sariverauthority-sara-tx.opendata.arcgis.com)** | Floodplains, water quality, the Mission Reach | Its own; cite the date you retrieved the data | [creek-levels](starters/creek-levels) |
| **[Alamo Area MPO](https://aampo-openmap-nexus-mpo.hub.arcgis.com)** | Funded road and transit projects, flood-exposed roads, bike stress | As-is disclaimer | [funded-projects](starters/funded-projects) |
| **Opportunity Home San Antonio** | 135 public and affordable housing communities: who each is for, homes, bedrooms, district | Informational use | [housing-near-you](starters/housing-near-you) |
| **[Edwards Aquifer Authority](https://data.edwardsaquifer.org)** | The aquifer's daily level, springflow, drought stage | Informational use, per layer | [aquifer-today](starters/aquifer-today) |

Plus the **U.S. Geological Survey**'s live gauges on the river and San Pedro Creek, every 15 minutes, in the public domain.

**[SOURCES.md](SOURCES.md)** is the full guide: what each agency publishes, the field names, and how to query each API. **[ATTRIBUTION.md](ATTRIBUTION.md)** has the exact credit line for each, to copy.

## 1 · Find: every dataset, in one list

[`data/catalog.json`](data) lists every public dataset from all seven, with its address, when it was last updated and its credit line, rebuilt every Monday by a GitHub Action. The same run checks every starter against its live source and opens an issue if one breaks.

To search it from the command line: `python3 starters/peek/main.py --find flood`. Peek searches every publisher at once, then shows any dataset's fields and first rows.

## 2 · Fetch: the starters

| Starter | Source | Build from it |
|---|---|---|
| [**Next bus**](starters/via-next-bus) | VIA | Type a stop, get the next buses. The bones of a departure board, a bot, or the transit app you wish existed. |
| [**Permits near you**](starters/permits-near-you) | City of San Antonio | Every building permit around a point since 2025, biggest first, with how long each took to issue. One SQL query to the City's API. |
| [**311 by district**](starters/311-by-district) | City of San Antonio | Half a million service calls, counted server-side in about two seconds. What each district calls about, and how often it closes late. |
| [**How we compare**](starters/how-we-compare) | City of San Antonio | San Antonio's economy beside seven peer metros: GDP growth, target industries, who owns the businesses, what the colleges graduate. |
| [**Funded projects**](starters/funded-projects) | Alamo Area MPO | The region's 68 funded road and transit projects for 2027–2030, totaled by the server, and the streets most exposed to a 100-year flood. |
| [**Creek levels**](starters/creek-levels) | USGS · River Authority | The river and San Pedro Creek right now, every 15 minutes, and whether a point sits in the River Authority's draft floodplains. Not a flood warning. |
| [**The aquifer today**](starters/aquifer-today) | Edwards Aquifer Authority · USGS | The J-17 well's level and 10-day average, the drought trigger it sits under, and springflow at Comal and San Marcos Springs. |
| [**Housing near you**](starters/housing-near-you) | Opportunity Home San Antonio · VIA | The housing authority's communities nearest a point: who each is for, homes and bedrooms, the year built. `--bus` adds how many buses an hour stop within a quarter mile. |
| [**Who represents me**](starters/who-represents-me) | Bexar County · City of San Antonio | Every district an address sits in, City Council to Congress, and the 2020 Census population around it. Takes a street address. |
| [**History: acequias and 1896–97**](starters/acequias) | Bexar County | The Spanish irrigation ditches from 1718, with a year slider; `--1897` maps 4,200 places from the 1896–97 city over today's streets. Data almost no other city has. |
| [**Peek**](starters/peek) | All seven | Search every publisher's datasets for a word, then see any one's fields and first rows. The way into the agencies nobody links to. |
| [**MCP**](starters/mcp) | All seven | San Antonio's open data as tools for your own coding agent: Claude Code, Codex, Cursor. One line of config. |

## 3 · Ask: bring your own agent

Using a coding agent? It's welcome here. [AGENTS.md](AGENTS.md) gives it the sources, the commands and the ground rules, so what it builds follows the same rules you would. Claude Code also picks up [the localhost skill](.claude/skills/localhost/SKILL.md) on its own, and [the MCP starter](starters/mcp) gives any agent the starters as tools.

**Next, steps 4 and 5:** an agent template you can ask in plain English. It writes the Python to answer, runs it in a sandbox rather than on your machine, and hands back the answer, a chart and the code. It isn't built yet; when it is, it'll be in `agents/`, with what it needs and what it costs said up front, since unlike the starters it will need an account and a model.

## What to build

Starters are the first commit, not the project. A few directions, any of which would be a strong portfolio piece or a Build-and-tell Friday post. Most are [open issues](https://github.com/devsanantonio/localhost/issues), so you can claim one:

- **Then and now.** Pick a block downtown and put the 1897 businesses next to what's there today.
- **Walk sheds.** Which neighborhoods are more than a quarter mile from a bus that comes every 15 minutes?
- **Your district's dashboard.** 311 calls by type and month for one council district, updated nightly with a GitHub Action.
- **A departure board** for a library, a coworking space or a dorm lobby.
- **Where the money goes.** The City's 370 bond projects and the Alamo Area MPO's funded projects for 2027–2030, on one map. Which run behind, and where?
- **When it rains.** The MPO's flood-exposed roads, the River Authority's floodplains and USGS's live creek levels. Which roads on your commute go under first?
- **One district, every publisher.** Pick a district, say Downtown West, and put permits, bond projects, flood-exposed streets, bike stress and bus stops on one page.
- **Something we haven't thought of.** Most of what's in [the catalog](data) has never been charted by anyone outside the agency that published it.

Maintained by [DEVSA](https://www.devsa.community), the nonprofit that connects the people building San Antonio tech. DEVSA isn't affiliated with any of these agencies, and nothing here speaks for them. The data is theirs. This is the way in.

## Build with care

Some of this data is about people. A few lines we hold to, and ask contributors to hold to as well:

- **No rankings of neighborhoods by crime.** The City publishes police calls, offenses and arrests. They're public, and there's real work to be done with them, but a "most dangerous neighborhoods" map built from raw counts tells a story about San Antonio that the data doesn't support. Starters here won't use them.
- **The 1897 directory is about real people.** It records names, jobs and, in the language of the time, race. Treat it as history — what the city was, who built it — not as a lookup of individuals.
- **Credit every source, every time.** It's the license, and it's how the people who publish this data find out it's being used.

## 6 · Return: show us what you built, tell us what's wrong

Built something with San Antonio data? Add it to [SHOWCASE.md](SHOWCASE.md) with a pull request: one line, a link to your repo or demo, and which sources it uses. Then share it in **#build-and-tell** on the [DEVSA Discord](https://www.devsa.community/discord) on a Friday.

Found a broken link, a stale dataset or a field that doesn't mean what its name says? [Open an issue](https://github.com/devsanantonio/localhost/issues). We collect these, and they're the most useful thing we can pass back to the people who publish the data.

## Contributing

New starters, better explanations of a dataset, and fixes are all welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

The code in this repo is [MIT](LICENSE). The data belongs to its publishers and is used under their terms. See [ATTRIBUTION.md](ATTRIBUTION.md).
