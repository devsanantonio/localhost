# San Antonio's acequias

Before San Antonio had streets it had acequias: irrigation ditches dug from the river and San Pedro Creek, starting in 1718. Bexar County maps every stretch, with the year it was dug and the year it was abandoned. This asks which ones ran near a point, then draws all of them on a map with a year slider.

```sh
python3 main.py                                        # near Geekdom, Houston and Soledad
python3 main.py --near 29.3621,-98.4794 --meters 300   # near Mission San José
open map.html        # macOS; on Windows `start map.html`, on Linux `xdg-open map.html`
```

```
Acequias within 400 m of 29.42637, -98.49337:
     76 m  San Pedro Acequia, dug 1718, dry by 1912  (Villa de San Fernando & Presidio de Bexar)
    321 m  Segundo Acequia, dug 1718, dry by 1719  (San Antonio de Valero)
```

The distance filter runs on the County's server (`geometry`, `distance`, `units`); the script only measures how close each ditch came. `map.html` is a self-contained Leaflet page: drag the slider and the ditches flowing in that year turn teal, the ones already dry turn gray.

## About the data

The County built this layer, and the others below, for San Antonio's Tricentennial. Its sixteen stretches belong to ten ditches: the Acequia Principal, the San Pedro and the short-lived Segundo from 1718; one for each of the five missions; the Upper Labor from 1776; and Francisco Arocha's private ditch. A ditch dug in sections, like the Alamo's, has a row per section with its own dates.

The same set of layers, all in the County's ArcGIS account, has what the ditches fed:

- **`Labores`**: the irrigated fields of each mission.
- **`300_GrantedLots`**: 348 Spanish land grants, with the grantee, the year and the labor it was in.
- **`Rullman_River`**: the river as these maps draw it, and **`SAMissions`**: the five missions.

## Where to take it

- **Your walk to work.** Which acequias did your route cross, and when did they go dry?
- **Then and now.** Lay the acequias under today's streets and see which ones still follow them.
- **The grants.** Join `300_GrantedLots` to the ditch that watered each lot, and chart who held land along it by year.

[Follow the water](https://www.devsa.community/localhost#bexar-county), on DEVSA's site, is built from these layers.

## Source

Bexar County Tricentennial layers, feature service `services1.arcgis.com/8onVmslF2KXErTHT/arcgis/rest/services/RullmanAcequia/FeatureServer/0`. Basemap tiles by Esri.

Data: Bexar County Information Technology GIS
