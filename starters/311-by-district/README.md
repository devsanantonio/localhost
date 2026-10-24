# 311 by district

Counts every 311 call in San Antonio by council district, and shows the share of each district's calls that closed after their service deadline. Then, for any one district, what people call about.

```sh
python3 main.py
python3 main.py --district 5
```

No download, no install: the City's 311 data is a live ArcGIS feature service, and the script asks it to do the counting (`groupByFieldsForStatistics` and `outStatistics`). The whole dataset is around half a million calls. Counting them server-side takes a second.

## Where to take it

- **Over time.** Add `OpenedDateTime` to the query and count by month. Does a district's late rate move?
- **On a map.** `XCOORD` and `YCOORD` are in Texas State Plane South Central (feet). Ask the service for `outSR=4326` to get latitude and longitude instead.
- **By department.** Swap `Category` for `Department`, `ReasonName` or `TypeName`.
- **Against people.** Calls per resident is fairer than raw calls. The County's census layers in this repo's README give you population to divide by.

## Fields

`Category`, `Department`, `ReasonName`, `TypeName`, `CaseStatus`, `OpenedDateTime`, `ClosedDateTime`, `SLADate` (the service deadline), `LateYesNo`, `SourceID` (how it was reported), `CouncilDistrict`, `XCOORD`, `YCOORD`, and `ObjectDescription`, which is usually the street address.

## Source

[311 Service Calls](https://data.sanantonio.gov/dataset/service-calls), City of San Antonio Open Data. Feature service: `services.arcgis.com/g1fRTDLeMgspWrYp/arcgis/rest/services/311_All_Service_Calls/FeatureServer/0`

Data: City of San Antonio Open Data, CC BY 4.0
