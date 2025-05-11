# My Setup:

```
PowerShell Extension v2025.0.0
Copyright (c) Microsoft Corporation.

https://aka.ms/vscode-powershell
Type 'help' to get help.

PS C:\TJ\SolarPan> systeminfo 

Host Name:                 TALHA-JAVED
OS Name:                   Microsoft Windows 10 Pro
OS Version:                10.0.19045 N/A Build 19045
OS Manufacturer:           Microsoft Corporation
OS Configuration:          Standalone Workstation
OS Build Type:             Multiprocessor Free
Registered Owner:          Lenovo
Registered Organization:
Product ID:                00330-51181-69926-AAOEM
Original Install Date:     4/11/2023, 6:40:13 AM
System Boot Time:          5/8/2025, 2:47:08 PM
System Manufacturer:       LENOVO
System Model:              20HEA0TLUS
System Type:               x64-based PC
Processor(s):              1 Processor(s) Installed.
                           [01]: Intel64 Family 6 Model 142 Stepping 9 GenuineIntel ~2611 Mhz
BIOS Version:              LENOVO N1QET98W (1.73 ), 12/26/2022
Windows Directory:         C:\WINDOWS
System Directory:          C:\WINDOWS\system32
Boot Device:               \Device\HarddiskVolume1
System Locale:             en-us;English (United States)
Input Locale:              en-us;English (United States)
Time Zone:                 (UTC+05:00) Islamabad, Karachi
Total Physical Memory:     15,987 MB
Available Physical Memory: 7,517 MB
Virtual Memory: Max Size:  23,127 MB
Virtual Memory: Available: 11,395 MB
Virtual Memory: In Use:    11,732 MB
Page File Location(s):     C:\pagefile.sys
Domain:                    WORKGROUP
Logon Server:              \\TALHA-JAVED
Hotfix(s):                 31 Hotfix(s) Installed.
                           [01]: KB5056578
                           [02]: KB5028853
                           [03]: KB5011048
                           [04]: KB5012170
                           [05]: KB5015684
                           [06]: KB5055612
                           [07]: KB5022924
                           [08]: KB5023794
                           [09]: KB5025315
                           [10]: KB5026879
                           [11]: KB5028318
                           [12]: KB5028380
                           [13]: KB5029709
                           [14]: KB5031539
                           [15]: KB5032392
                           [16]: KB5032907
                           [17]: KB5034224
                           [18]: KB5036447
                           [19]: KB5037018
                           [20]: KB5037240
                           [21]: KB5037995
                           [22]: KB5039336
                           [23]: KB5041579
                           [24]: KB5043935
                           [25]: KB5043130
                           [26]: KB5046823
                           [27]: KB5050388
                           [28]: KB5050111
                           [29]: KB5052916
                           [30]: KB5054682
                           [31]: KB5055663
Network Card(s):           2 NIC(s) Installed.
                           [01]: Intel(R) Ethernet Connection (4) I219-LM
                                 Connection Name: Ethernet
                                 Status:          Media disconnected
                           [02]: Intel(R) Dual Band Wireless-AC 8265
                                 Connection Name: Wi-Fi
                                 DHCP Enabled:    Yes
                                 DHCP Server:     192.168.100.1
                                 IP address(es)
                                 [01]: 192.168.100.21
                                 [02]: fe80::dbfd:b76:39cb:5f86
                                 [03]: 2406:d00:cccd:fe2f:c0a:830b:bdb3:5d6c    
                                 [04]: 2406:d00:cccd:fe2f:d7f0:5b55:2f7a:557b   
Hyper-V Requirements:      A hypervisor has been detected. Features required for Hyper-V will not be displayed.
PS C:\TJ\SolarPan> 
```

- Windows 10
    
- VS Code
    
- Github
    
- OSGeo4W Shell (✔ now embedded in VS Code)
    

### What I really need are these:

- **Objectnummer**
    
- **Street**
    
- **Housenumber**
    
- **Postal code**
    
- **City**
    
- **Country**
    
- **Gebruiksdoel**
    
- **Functie**
    
- **Google maps link URL** (📍 next step)
    
- **Longitude LNG**
    
- **Latitude LAT**
    

### Current Task: Google Maps Pin Links ✅

We’re now at the stage where we embed Google Maps URLs using centroid coordinates for each building.

---

### Checkpoint Workflow: Google Maps Pin Links

Break down into granular checkpoints—run each, confirm output, then move on.

**Checkpoint 1: Centroid Extraction & CSV Preview**

```
ogrinfo -ro bag-light.gpkg -sql "SELECT identificatie, ST_X(ST_Centroid(geom)) AS LNG, ST_Y(ST_Centroid(geom)) AS LAT FROM pand LIMIT 5"
```

- ✅ Expect 5 rows of `identificatie`, `LNG`, `LAT` in RD New projection.
    
- ❓ Confirm you see valid numeric values.
    

**Checkpoint 2: Address Fields Preview**

```
ogrinfo -ro bag-light.gpkg -sql "SELECT pand_identificatie, openbare_ruimte_naam AS street, huisnummer, postcode, woonplaats_naam AS city FROM verblijfsobject LIMIT 5"
```

- ✅ Expect 5 address rows matching `pand_identificatie` to buildings.
    
- ❓ Confirm street names, house numbers, and city values.
    

**Checkpoint 3: Merge Preview (RD New)**

```
ogrinfo -ro bag-light.gpkg -sql "SELECT p.identificatie AS Objectnummer, s.street, s.huisnummer, s.postcode, s.city, ST_X(ST_Centroid(p.geom)) AS LNG, ST_Y(ST_Centroid(p.geom)) AS LAT FROM pand p JOIN (SELECT pand_identificatie, openbare_ruimte_naam AS street, huisnummer, postcode, woonplaats_naam AS city FROM verblijfsobject) s ON p.identificatie = s.pand_identificatie LIMIT 5"
```

- ✅ Expect combined 5 rows with all fields in RD New.
    
- ❓ Confirm that `Objectnummer` matches `pand_identificatie`.
    

**Checkpoint 4a: Small Batch Export with Progress**

```
ogr2ogr -f CSV solar_addresses_part.csv -progress -skipfailures -sql "SELECT p.identificatie AS Objectnummer, s.openbare_ruimte_naam AS street, s.huisnummer, s.postcode, s.woonplaats_naam AS city, ST_X(ST_Centroid(p.geom)) AS LNG, ST_Y(ST_Centroid(p.geom)) AS LAT, 'Nederland' AS Country FROM pand p JOIN verblijfsobject s ON p.identificatie = s.pand_identificatie LIMIT 10000" bag-light.gpkg
```

- ✅ Exports first 10k rows into `solar_addresses_part.csv` quickly, showing percentage progress.
    
- ❓ Check file and progress output to confirm speed.
    

**Checkpoint 4b: Full Export with Detailed Logging & Resume**

```
ogr2ogr --verbose -progress -skipfailures -append -f CSV solar_addresses.csv -sql "SELECT p.identificatie AS Objectnummer, s.openbare_ruimte_naam AS street, s.huisnummer, s.postcode, s.woonplaats_naam AS city, ST_X(ST_Centroid(p.geom)) AS LNG, ST_Y(ST_Centroid(p.geom)) AS LAT, 'Nederland' AS Country FROM pand p JOIN verblijfsobject s ON p.identificatie = s.pand_identificatie" bag-light.gpkg >ogr2ogr.log 2>&1
```

- `--verbose` prints detailed internal messages.
    
- `-progress` shows percentage progress.
    
- `-skipfailures` skips problematic features without stopping.
    
- `-append` allows resuming the export if re-run.
    
- Redirection `>ogr2ogr.log 2>&1` captures both output and errors in `ogr2ogr.log`.
    

**Checkpoint 4c: Random Sample Validation**

```
# PowerShell sample 10 random lines (skip header)
powershell -Command "Get-Content solar_addresses.csv | Select-Object -Skip 1 | Get-Random -Count 10"
```

```
# Bash (if shuf available)
shuf -n 10 solar_addresses.csv
```

- ✅ This outputs 10 random data rows for quick validity check.
    
- ❓ Confirm that sampled lines have correct Objectnummer, street, postcode, and coordinates.
    

> **Note:** `solar_addresses.csv` does **not** include the `maps_url` column. The Google Maps link URL is generated in **Checkpoint 5** when reprojecting to WGS84.

**Checkpoint 5: Reproject & URL Preview (SQLite Dialect)**

```
ogr2ogr -f CSV solar_addresses_wgs84.csv -dialect sqlite -sql "SELECT Objectnummer, street, huisnummer, postcode, city, Country, ST_X(ST_Transform(MakePoint(LNG, LAT),4326)) AS Longitude, ST_Y(ST_Transform(MakePoint(LNG, LAT),4326)) AS Latitude, 'https://maps.google.com/?q=' || ST_Y(ST_Transform(MakePoint(LNG, LAT),4326)) || ',' || ST_X(ST_Transform(MakePoint(LNG, LAT),4326)) AS maps_url FROM solar_addresses" solar_addresses.csv
```

- **Run this in the OSGeo4W Shell** (so `ogr2ogr` is on PATH).
    
- The `-dialect sqlite` flag enables spatial functions on CSV.
    

> After it finishes, use `head -n 10 solar_addresses_wgs84.csv` (or PowerShell `Get-Content -TotalCount 10`) to verify coordinates and maps URLs.

---

### 📝 Observation & Next Actions

- **Observation:** Running Checkpoint 5 shows the `maps_url` column remains empty.
    
- **Next:** We will debug the SQL syntax or data workflow to correctly populate Google Maps URLs in a later step.
    

# Next steps:

We’ll start by testing the PDOK Zonatlas WFS API in small increments, before downloading full datasets.

#### Step A0: Test WFS Host Connectivity

- **Action:** Check DNS resolution and reachability of the PDOK WFS host.
    
- **Commands (PowerShell):**
    
    ```
    nslookup geodata.nationaalgeoregister.nl
    ping geodata.nationaalgeoregister.nl
    ```
    
- **Goal:** Confirm the host resolves to an IP and is pingable. If these commands fail, your network or DNS is blocking access.
    

#### Step A0b: Manual Download Fallback

- **Action:** If the WFS endpoint is unreachable, manually download the shapefile via browser.
    
- **Instructions:**
    
    1. Open [https://geodata.nationaalgeoregister.nl/solar](https://geodata.nationaalgeoregister.nl/solar) in your browser.
        
    2. Click “Download” and choose **ESRI Shapefile** format.
        
    3. Save `zonnepanelen.zip` into your working directory (`C:\TJ\SolarPan`).
        
- **Goal:** Obtain the shapefile locally without CLI download.
    

#### Step A1: GetCapabilities

- **Action:** Retrieve WFS capabilities with explicit parameters.
    
- **Command:**
    
    ```
    curl "http://geodata.nationaalgeoregister.nl/solar/ows?service=WFS&version=2.0.0&request=GetCapabilities"
    ```
    
- **Goal:** Inspect available `FeatureTypeList` to confirm the layer name (`zonnepanelen`).
    
- **Action:** Retrieve WFS capabilities with explicit parameters.
    
- **Command:**
    
    ```
    curl "http://geodata.nationaalgeoregister.nl/solar/ows?service=WFS&version=2.0.0&request=GetCapabilities"
    ```
    
- **Goal:** Inspect available `FeatureTypeList` to confirm the layer name (`zonnepanelen`).
    

#### Step A2: Preview Feature Count

- **Action:** Request a small number of features in JSON to test the query.
    
- **Command:**
    
    ```
    curl "http://geodata.nationaalgeoregister.nl/solar/ows?service=WFS&version=2.0.0&request=GetFeature&typeNames=zonnepanelen&count=5&outputFormat=application/json"
    ```
    
- **Goal:** Get 5 features back in JSON, verify fields like `id` and `aantal_panelen` exist.
    

#### Step A3: Download Shapefile (ZIP)

- **Action:** Download the full shapefile once endpoint is confirmed.
    
- **Command:**
    
    ```
    curl -L -o zonnepanelen.zip "http://geodata.nationaalgeoregister.nl/solar/ows?service=WFS&version=2.0.0&request=GetFeature&typeNames=zonnepanelen&outputFormat=shape-zip"
    ```
    
- **Goal:** Obtain `zonnepanelen.zip` for local processing.
    

---

### Local Shapefile Workflow

Once the above tests succeed, proceed with:

**Step B1: Extract & Inspect Layers**

- **Commands:**
    
    ```
    tar -xf zonnepanelen.zip -C zonnepanelen
    ogrinfo zonnepanelen/zonnepanelen.shp -so
    ```
    

**Step B2: Count Intersecting Buildings** ... (unchanged steps)

We’ll download the PDOK “zonnepanelen” layer as a shapefile and then process it locally.

**Step A1: Download Solar Panel Shapefile from PDOK WFS**

- **Action:** Request the `zonnepanelen` layer in ESRI shapefile format.
    
- **Command (CMD / PowerShell):**
    
    ```
    curl -L -o zonnepanelen.zip "http://geodata.nationaalgeoregister.nl/solar/ows?service=WFS&version=2.0.0&request=GetFeature&typeNames=zonnepanelen&outputFormat=shape-zip"
    ```
    
- **Goal:** Have `zonnepanelen.zip` containing `zonnepanelen.shp` etc.
    

**Step A2: Extract & Inspect Layers**

- **Action:** Unzip and list layer metadata.
    
- **Commands (CMD / PowerShell):**
    
    ```
    tar -xf zonnepanelen.zip -C zonnepanelen
    ogrinfo zonnepanelen/zonnepanelen.shp -so
    ```
    
- **Goal:** Confirm layer name, geometry type, and key attributes like `id` and `aantal_panelen`.
    

**Step A3: Count Intersecting Buildings**

- **Action:** Count BAG buildings intersecting panel footprints.
    
- **Command:**
    
    ```
    ogrinfo -ro bag-light.gpkg -sql "SELECT COUNT(DISTINCT p.identificatie) AS cnt FROM pand p JOIN zonnepanelen/zonnepanelen.shp s ON ST_Intersects(p.geom, s.geometry)"
    ```
    
- **Goal:** Get approximate count of buildings with panels.
    

**Step A4: Export Panelled Building IDs**

- **Action:** Extract unique BAG IDs of panelled buildings.
    
- **Command:**
    
    ```
    ogr2ogr -f CSV buildings_with_panels.csv -sql "SELECT DISTINCT p.identificatie AS Objectnummer FROM bag-light.gpkg p JOIN zonnepanelen/zonnepanelen.shp s ON ST_Intersects(p.geom, s.geometry)" bag-light.gpkg
    ```
    
- **Goal:** `buildings_with_panels.csv` listing `Objectnummer` of panelled buildings.
    

**Step A5: Merge Panel Info into Address List**

- **Action:** Annotate address CSV with a `has_panels` flag.
    
- **Command (SQLite dialect):**
    
    ```
    ogr2ogr -f CSV solar_addresses_final.csv -dialect sqlite -sql "SELECT a.*, CASE WHEN b.Objectnummer IS NOT NULL THEN 1 ELSE 0 END AS has_panels FROM 'csv/solar_addresses.csv' a LEFT JOIN 'csv/buildings_with_panels.csv' b ON a.Objectnummer = b.Objectnummer" csv
    ```
    
- **Goal:** `solar_addresses_final.csv` with `has_panels` = 1/0 per building.
    

> Run **Step A1** to download and confirm the shapefile, then proceed to **Step A2**.**

- **Action:** Preview the `zonnepanelen` layer from PDOK’s WFS.
    
- **Command (OSGeo4W Shell):**
    
    ```
    ogrinfo WFS:"http://geodata.nationaalgeoregister.nl/solar/ows?service=WFS&version=2.0.0&request=GetCapabilities" zonnepanelen -so
    ```
    

# Note: Use HTTP (not HTTPS) or verify network/DNS connectivity to resolve the PDOK WFS host.

````
- **Goal:** Confirm layer name `zonnepanelen` and geometry (likely polygons representing panel areas).

**Step A2: Sample Panel Features**
- **Action:** Fetch a small sample of solar panel features.
- **Command (OSGeo4W Shell):**
```cmd
ogrinfo WFS:"https://geodata.nationaalgeoregister.nl/solar/ows" -sql "SELECT id, naam, aantal_panelen, geom FROM zonnepanelen LIMIT 5"
````

- **Goal:** Verify attributes such as `id`, `aantal_panelen` and geometry type.
    

**Step A3: Count Intersecting Buildings**

- **Action:** Count how many BAG buildings intersect any panel footprint.
    
- **Command:**
    
    ```
    ogrinfo -ro bag-light.gpkg -sql "SELECT COUNT(DISTINCT p.identificatie) AS cnt FROM pand p JOIN WFS:'https://geodata.nationaalgeoregister.nl/solar/ows' zonnepanelen s ON ST_Intersects(p.geom, s.geom)"
    ```
    
- **Goal:** Get an approximate count of panelled buildings.
    

**Step A4: Export Panelled Building IDs**

- **Action:** Extract unique BAG IDs of buildings with panels.
    
- **Command:**
    
    ```
    ogr2ogr -f CSV buildings_with_panels.csv -sql "SELECT DISTINCT p.identificatie AS Objectnummer FROM bag-light.gpkg p JOIN WFS:'https://geodata.nationaalgeoregister.nl/solar/ows' zonnepanelen s ON ST_Intersects(p.geom, s.geom)" bag-light.gpkg
    ```
    
- **Goal:** Create `buildings_with_panels.csv` listing `Objectnummer` of panelled buildings.
    

**Step A5: Merge Panel Info into Address List**

- **Action:** Annotate your main CSV with a `has_panels` flag.
    
- **Command (SQLite dialect):**
    
    ```
    ogr2ogr -f CSV solar_addresses_final.csv -dialect sqlite -sql "SELECT a.*, CASE WHEN b.Objectnummer IS NOT NULL THEN 1 ELSE 0 END AS has_panels FROM 'csv/solar_addresses.csv' a LEFT JOIN 'csv/buildings_with_panels.csv' b ON a.Objectnummer = b.Objectnummer" csv
    ```
    
- **Goal:** Generate `solar_addresses_final.csv` with buildings flagged (`has_panels` = 1/0).
    

> Run **Step A1** to preview the WFS layer and confirm connectivity, then proceed to **Step A2**.

# Solar Panel Verification Workflow – Overpass API Approach

We’ll shift from the unreachable PDOK WFS to a low‑latency, open source that reliably covers the Netherlands: **OpenStreetMap via Overpass API**. OSM already contains many rooftop solar installations crowdsourced by mappers; extraction is a single HTTP query—no DNS issues, no zip downloads.

---

## Why Overpass API?

- ✅ **Global Coverage** – includes North Holland without regional throttling.
    
- ✅ **Simple HTTP GET** – works behind most firewalls.
    
- ✅ **Direct GeoJSON** – no need for complex parsing.
    
- ❕ Completeness varies by area, but North Holland (Amsterdam region) is well mapped.
    

---

## Incremental Checkpoints

### Checkpoint O1 – Ping Overpass

```
curl -G "https://overpass-api.de/api/interpreter" --data-urlencode "data=[out:json][timeout:25];node(52.5,4.5,53.2,5.5)[\"generator:source\"=\"solar\"];out 1;"
```

**Goal:** Return a tiny JSON with at least one solar node – proves connectivity.

---

### Checkpoint O2 – Download North Holland Solar Objects  ✅ **Completed**

```
curl -o nh_solar.json -G "https://overpass-api.de/api/interpreter" --data-urlencode "data=[out:json][timeout:600];(node(52.5,4.5,53.2,5.5)[\"generator:source\"=\"solar\"];way(52.5,4.5,53.2,5.5)[\"generator:source\"=\"solar\"];relation(52.5,4.5,53.2,5.5)[\"generator:source\"=\"solar\"];);out geom;"
```

- `nh_solar.json` is **saved** (≈ {{SIZE_MB}} MB, {{ELEMENTS}} solar objects).
    
- Sanity check:
    
    ```
    jq '.elements | length' nh_solar.json  # count features
    jq '.elements[0]' nh_solar.json        # peek first feature
    ```
    

---

### Checkpoint O3 – Convert JSON → GeoJSON

```
ogr2ogr -f GeoJSON nh_solar.geojson nh_solar.json
```

**Goal:** Produce `nh_solar.geojson` ready for spatial joins.

After running, confirm file exists and inspect:

```
ogrinfo -ro nh_solar.geojson -summary
```

## If OK, reply _Checkpoint 3 done_, and we’ll proceed to the intersection step (O4).

### Checkpoint O3 – Convert to GeoJSON

```
ogr2ogr -f GeoJSON nh_solar.geojson nh_solar.json
```

**Goal:** GeoJSON ready for spatial join with BAG geometries.

---

### Checkpoint O4 – Intersect with BAG Buildings

```
ogr2ogr -f CSV buildings_with_panels.csv -sql "SELECT DISTINCT p.identificatie AS Objectnummer FROM bag-light.gpkg p JOIN nh_solar.geojson s ON ST_Intersects(p.geom, s.geometry)" bag-light.gpkg
```

**Goal:** `buildings_with_panels.csv` listing only BAG IDs that intersect at least one solar object.

---

### Checkpoint O5 – Merge Flag into Address CSV

```
ogr2ogr -f CSV solar_addresses_final.csv -dialect sqlite -sql "SELECT a.*, CASE WHEN b.Objectnummer IS NOT NULL THEN 1 ELSE 0 END AS has_panels FROM 'csv/solar_addresses.csv'.solar_addresses a LEFT JOIN 'csv/buildings_with_panels.csv'.buildings_with_panels b ON a.Objectnummer = b.Objectnummer" csv
```

**Goal:** `solar_addresses_final.csv` gains `has_panels` (1/0).

---

### Checkpoint O6 – Random Spot‑Check

```
Get-Content solar_addresses_final.csv | Select-Object -Skip 1 | Get-Random -Count 10
```

Verify a few addresses with `has_panels=1` visually on Google Maps satellite.

---

## Quick Suitability Snapshot of User‑Supplied Links

|SourceGlobal?NL CoverageProsCons|||||
|---|---|---|---|---|
|**Overpass API (OSM)**|🌍|✅|Real‑time, free, easy|Crowdsourced completeness varies|
|Deep Solar (Kaggle)|🇺🇸|❌|High‑res US rooftops|US‑only ([kaggle.com](https://www.kaggle.com/datasets/chaitanyakumar12/time-series-forecasting-of-solar-energy?utm_source=chatgpt.com))|
|Roofpedia|🌍|✅*|DL‑derived global dataset|Still research‑stage, may need cleanup ([github.com](https://github.com/satellite-image-deep-learning/techniques?utm_source=chatgpt.com))|
|OpenPV (NREL)|🇺🇸|❌|Installation metadata|US‑only, no geometry ([medium.com](https://medium.com/towards-data-science/estimating-solar-panel-output-with-open-source-data-bbca6ea1f523?utm_source=chatgpt.com))|
|Zenodo 5171712|🌍 (samples)|⚠|Good training imagery|Not exhaustive; imagery tiles only ([zenodo.org](https://zenodo.org/records/5171712?utm_source=chatgpt.com))|
|Kaggle salimhammadi07|🌍 (samples)|⚠|Segmentation masks|Same as Zenodo; subset ([kaggle.com](https://www.kaggle.com/datasets/salimhammadi07/solar-panel-detection-and-identification?utm_source=chatgpt.com))|

> **Proceed with Checkpoint O1** to verify Overpass response, then let’s walk through the subsequent steps.

## 2025‑05‑11 Update

- **Decision:** Re‑issue the Overpass request with `[out:xml]` to download an `.osm` XML file (`nh_solar.osm`). GDAL’s OSM driver can read XML natively, so this avoids installing extra converters like _osmtogeojson_.
    
- **New step O3a** (download):
    
    ```cmd
    curl -o nh_solar.osm -G "https://overpass-api.de/api/interpreter" ^
         --data-urlencode "data=[out:xml][timeout:600];
           (node(52.5,4.5,53.2,5.5)['generator:source'='solar'];
            way(52.5,4.5,53.2,5.5)['generator:source'='solar'];
            relation(52.5,4.5,53.2,5.5)['generator:source'='solar'];);
           out geom;"
    ```
    
- **New step O3b** (convert + re‑project):
    
    ```cmd
    ogr2ogr -f GPKG nh_solar_rd.gpkg nh_solar.osm ^
            -t_srs EPSG:28992 -nln solar_rd -progress
    ```
    
- Checkpoints **O4** (BAG intersection) and **O5** (merge flag) stay the same.
    
- Reminder: use `-verbose` (single dash); `--verbose` isn’t recognised in OSGeo4W GDAL.
    

---

### Checkpoint 3c: **Validate **`` 🔍

**Goal:** Ensure the GeoPackage holds solar objects in RD New and covers North Holland.

1. **Layer & feature summary**
    
    ```cmd
    ogrinfo -ro nh_solar_rd.gpkg -summary
    ```
    
    - ✅ Expect a layer called `solar_rd` (or similar) with a feature count > 0 and SRS `EPSG:28992`.
        
2. **Quick attribute peek (first 5)**
    
    ```cmd
    ogrinfo nh_solar_rd.gpkg solar_rd -al -limit 5
    ```
    
    - ✅ Confirm you see tags like `generator:source=solar` or `power=generator`.
        
3. **Bounding‑box sanity**
    
    ```cmd
    ogrinfo nh_solar_rd.gpkg solar_rd -al -geom=SUMMARY -q | find "Extent"
    ```
    
    - ✅ Extent X ≈ 85 000–150 000, Y ≈ 475 000–520 000.
        
4. **Count by geometry type**
    
    ```cmd
    ogrinfo -ro nh_solar_rd.gpkg -sql "SELECT ST_GeometryType(geometry) AS gtype, COUNT(*) AS n FROM solar_rd GROUP BY gtype"
    ```
    
5. **Spot‑check attribute filter**
    
    ```cmd
    ogrinfo -ro nh_solar_rd.gpkg -sql "SELECT id, tags->'generator:source' AS src FROM solar_rd WHERE tags->'generator:source' IS NOT NULL LIMIT 10"
    ```
    

> **Troubleshooting – ‘attempt to write a readonly database’

If you still see this error after `attrib -R` and closing Explorer/VS Code previews:

|Fix step|Command|Why it helps|
|---|---|---|
|**a. Drop **``** flag**|`ogrinfo nh_solar_rd.gpkg -summary`|Allows GDAL to create missing metadata tables.|
|**b. Safe read‑only probe**|`gdalinfo nh_solar_rd.gpkg`|Confirms file is readable without any writes.|
|**c. Suppress metadata creation**|`ogrinfo --config OGR_GPKG_NO_CREATE_METADATA YES nh_solar_rd.gpkg -summary`|Tells GDAL not to attempt writing `gpkg_metadata` tables at all.|
|**d. Repair metadata**|```cmd||
|sqlite3 nh_solar_rd.gpkg "CREATE TABLE IF NOT EXISTS gpkg_metadata (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, md_scope TEXT NOT NULL, md_standard_uri TEXT NOT NULL, mime_type TEXT NOT NULL, metadata TEXT NOT NULL);"|||

````|
| **e. Re‑export w/out metadata** | `ogr2ogr -f GPKG nh_solar_rd_fix.gpkg nh_solar.osm -t_srs EPSG:28992 -nln solar_rd -dsco METADATA=NO -progress` | Generates a GeoPackage that won’t trigger metadata writes. |

Proceed down the list until one works, then re‑run the validation commands.


## 2025‑05‑11 Fallback Path — Skip GeoPackage
When GeoPackage metadata issues refuse to clear, switch to a **GeoJSON‑only** workflow (no internal SQLite writes):

### Fallback O3′ – Convert & Re‑project to GeoJSON in RD New
```cmd
REM Requires Node (osmtogeojson) — install once if needed  *(npm may print a **deprecated @xmldom/xmldom** warning; it’s harmless and the install still works)*
npm i -g osmtogeojson

REM 1 Convert Overpass JSON → GeoJSON  (explicit `-o` avoids > redirection issues)
osmtogeojson nh_solar.json -o nh_solar_raw.geojson
REM confirm: for %F in (nh_solar_raw.geojson) do @echo %F %%~zF bytes

REM 2 Re‑project to RD New (EPSG 28992)  — 👉 **single‑line** to avoid CMD caret pitfalls
ogr2ogr -f GeoJSON nh_solar_rd.geojson nh_solar_raw.geojson -t_srs EPSG:28992 -progress
````

**Multiline tip:** If you prefer a line break, end the first line with a caret `^` **with no trailing spaces**:

```cmd
ogr2ogr -f GeoJSON nh_solar_rd.geojson nh_solar_raw.geojson ^
  -t_srs EPSG:28992 -progress
```

_CMD prints **`More?`** when the caret is parsed correctly; if you press Enter before typing the rest, re‑type the command or use one line._

### Fallback O4′ – Intersect BAG ↔ GeoJSON directly

```cmd
ogr2ogr -f CSV buildings_with_panels.csv bag-light.gpkg ^
  -dialect sqlite ^
  -sql "SELECT DISTINCT p.identificatie AS Objectnummer
        FROM pand p
        JOIN 'nh_solar_rd.geojson'.OGRGeoJSON s
          ON ST_Intersects(p.geom, s.geometry)" ^
  -progress -skipfailures
```

### Fallback O5′ – Merge flag (unchanged)

```cmd
ogr2ogr -f CSV solar_addresses_final.csv -dialect sqlite ^
  -sql "SELECT a.*, CASE WHEN b.Objectnummer IS NOT NULL THEN 1 ELSE 0 END AS has_panels
        FROM 'csv/solar_addresses.csv'.solar_addresses a
        LEFT JOIN 'csv/buildings_with_panels.csv'.buildings_with_panels b
          ON a.Objectnummer = b.Objectnummer" ^
  csv
```

➡ No metadata tables are touched, so the read‑only error disappears.

### Quick sanity commands

```cmd
REM confirm GeoJSON file size
for %F in (nh_solar_raw.geojson nh_solar_rd.geojson) do @echo %F %%~zF bytes

REM peek first feature
ogrinfo nh_solar_raw.geojson -limit 1
```

If `ogr2ogr` still can’t open `nh_solar_raw.geojson`, check that the file actually contains `{` / `[` at the top (use `type nh_solar_raw.geojson | more`). Empty/0‑byte files indicate `osmtogeojson` failed — rerun it or use `osmtogeojson -o nh_solar_raw.geojson nh_solar.json`.

### 2025‑05‑11 One‑Liner Commands _(latest fix: **`area_tags`** to keep solar polygons)_ — separated snippets _(now with **`CONFIG_FILE`** to keep solar tags)_

_(If **`ogrinfo nh_solar_rd.geojson -summary`** later shows ****“Unterminated array”****, see the troubleshooting box right below these snippets.)_

**1. Download OSM XML**

```cmd
curl -o nh_solar.osm -G "https://overpass-api.de/api/interpreter" --data-urlencode "data=[out:xml][timeout:600];(node(52.5,4.5,53.2,5.5)['generator:source'='solar'];way(52.5,4.5,53.2,5.5')['generator:source'='solar'];relation(52.5,4.5,53.2,5.5')['generator:source'='solar'];);out geom;"
```

**2. Size check**

```cmd
for %F in (nh_solar.osm) do @echo %F %~zF bytes
```

**3. Convert & re‑project to GeoJSON (RD New)**

```cmd
ogr2ogr -overwrite -f GeoJSON nh_solar_rd.geojson nh_solar.osm -t_srs EPSG:28992 -nln solar_rd -progress
```

**4. Layer summary sanity**

```cmd
ogrinfo nh_solar_rd.geojson -summary
```

**5. Extract buildings with panels**

```cmd
ogr2ogr -overwrite -f CSV buildings_with_panels.csv bag-light.gpkg -dialect sqlite -sql "SELECT DISTINCT p.identificatie AS Objectnummer FROM pand p JOIN 'nh_solar_rd.geojson'.OGRGeoJSON s ON ST_Intersects(p.geom, s.geometry)" -progress -skipfailures
```

**6. Merge panel flag into addresses**

```cmd
ogr2ogr -overwrite -f CSV solar_addresses_final.csv -dialect sqlite -sql "SELECT a.*, CASE WHEN b.Objectnummer IS NOT NULL THEN 1 ELSE 0 END AS has_panels FROM 'csv/solar_addresses.csv'.solar_addresses a LEFT JOIN 'csv/buildings_with_panels.csv'.buildings_with_panels b ON a.Objectnummer = b.Objectnummer" csv
```

---

### Troubleshooting: “Unterminated array / Failed to read GeoJSON”

|Cause|Fix|
|---|---|
|**GeoJSON file truncated** (conversion aborted early or disk full)|Delete the bad file and re‑run **step 3** (use `-overwrite` as above). Check file size > 100 KB before running `ogrinfo`.|
|Overpass XML contains **tags with invalid UTF‑8** causing ogr2ogr to abort mid‑write|Add `--config OGR_OSM_OPTIONS "USE_POINT=YES"` to step 3:`ogr2ogr --config OGR_OSM_OPTIONS "USE_POINT=YES" -overwrite -f GeoJSON …`|
|Accidentally opened GeoJSON in editor while converting (file lock)|Close the file in VS Code / other apps, delete it, re‑run step 3.|
|Running conversion in **PowerShell** where back‑ticks or quotes got stripped|Copy the one‑liner exactly; if in doubt, switch to **cmd.exe** prompt inside OSGeo4W.|

After a fresh step 3, re‑check with:

```cmd
for %F in (nh_solar_rd.geojson) do @echo %F %~zF bytes
ogrinfo nh_solar_rd.geojson -summary
```

A non‑zero file size and successful summary mean the GeoJSON is valid; proceed to step 5.

---

### 2025‑05‑11 GeoJSON → GPKG One‑Liner

```cmd
ogr2ogr -overwrite -f GPKG nh_solar_rd.gpkg nh_solar_wgs84.geojson -s_srs EPSG:4326 -t_srs EPSG:28992 -nln solar_rd -nlt GEOMETRY -progress
```

- `` — assume source GeoJSON is WGS‑84 (osmtogeojson default)
    
- `` — lets GDAL mix polygons, lines, points into one layer
    

**Verify**

```cmd
ogrinfo nh_solar_rd.gpkg solar_rd -summary
```

Feature Count should be **> 0**. Then run the BAG‑intersection SQL exactly as before, replacing layer names with ``.

## 2025‑05‑11 Simplified City‑by‑City Workflow (using **bag‑nh.gpkg**) 🟢

### Performance note – JSON vs CSV for final step

- **GeoJSON (or OSM‑JSON)** is only needed while we carry geometry for the spatial intersect. Once the `has_panels` flag is derived, we no longer need geometries.
    
- **CSV** writes fastest, uses the least RAM, and opens instantly in Excel ‑‑ ideal for the **final deliverable**.
    
- Therefore: **keep solar geometries in GeoJSON/GPKG only until the intersect is done**, then export the merged table to CSV.
    
- If you ever need to reload into QGIS, you can still drag‑drop the CSV (it autogeocodes from the Longitude / Latitude columns).
    

We already have `` — Noord‑Holland buildings pre‑clipped and re‑projected. The minimal pipeline per city is now:

### 1 Export BAG rows for a single city (e.g. Haarlem)

```cmd
ogr2ogr -overwrite -f CSV haarlem_bag.csv bag-nh.gpkg \
  -dialect sqlite \
  -sql "SELECT p.identificatie        AS Objectnummer,
               s.openbare_ruimte_naam AS street,
               s.huisnummer,
               s.postcode,
               s.woonplaats_naam     AS city,
               'Nederland'           AS Country,
               ST_X(ST_Centroid(p.geom)) AS LNG,
               ST_Y(ST_Centroid(p.geom)) AS LAT
        FROM pand p
        JOIN verblijfsobject s ON p.identificatie = s.pand_identificatie
        WHERE s.woonplaats_naam = 'Haarlem'"
```

### 2 Download city solar objects via Overpass (bbox)

```cmd
curl -o haarlem_solar.json -G "https://overpass-api.de/api/interpreter" --data-urlencode "data=[out:json][timeout:180];(node[\"generator:source\"=\"solar\"](52.350,4.595,52.450,4.715);way[\"generator:source\"=\"solar\"](52.350,4.595,52.450,4.715);relation[\"generator:source\"=\"solar\"](52.350,4.595,52.450,4.715););out geom;"
```

### 3 Convert JSON → GeoJSON and re‑project on‑the‑fly during intersect

```cmd
osmtogeojson haarlem_solar.json -o haarlem_solar.geojson
```

### 4 Intersect BAG vs solar

```cmd
ogr2ogr -overwrite -f CSV haarlem_buildings_with_panels.csv bag-nh.gpkg \
  -dialect sqlite \
  -sql "SELECT DISTINCT p.identificatie AS Objectnummer
        FROM pand p
        JOIN 'haarlem_solar.geojson'.OGRGeoJSON s
          ON ST_Intersects(p.geom, Transform(s.geometry, 28992))
        WHERE p.woonplaats_naam = 'Haarlem'"
```

### 5 Merge `has_panels` flag into address CSV

```cmd
ogr2ogr -overwrite -f CSV haarlem_final.csv -dialect sqlite \
  -sql "SELECT a.*, CASE WHEN b.Objectnummer IS NOT NULL THEN 1 ELSE 0 END AS has_panels
        FROM 'haarlem_bag.csv'.haarlem_bag a
        LEFT JOIN 'haarlem_buildings_with_panels.csv'.haarlem_buildings_with_panels b
          ON a.Objectnummer = b.Objectnummer"
```

➡ Run steps **1–5** for Haarlem, then repeat with new bbox / city name (Amsterdam, Zaanstad, …). No GeoPackage edits, no metadata hiccups.