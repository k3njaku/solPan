#!/usr/bin/env python3
"""
script.py

Enriches solar_buildings_final_with_pin_links.csv by:
  - Merging in Functie from ZONNEPANELEN.csv
  - Fetching OSM business tags via Overpass API
  - Reverse-geocoding via Nominatim to get feature type
Writes solar_buildings_with_osm_and_functie.csv (first 5 rows for testing).
"""

import pandas as pd
import requests
import time

# CONFIGURATION
INPUT_CSV     = "solar_buildings_final_with_pin_links.csv"
PANEL_CSV     = "ZONNEPANELEN.csv"
OUTPUT_CSV    = "solar_buildings_with_osm_and_functie.csv"
OVERPASS_URL  = "https://overpass-api.de/api/interpreter"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"
RADIUS_M      = 10    # Overpass search radius in meters
PAUSE_S       = 1.0   # polite pause between API calls

def fetch_osm_business(lat, lon, radius=RADIUS_M):
    """
    Query Overpass for amenity/shop/office around (lat, lon).
    Returns (name, tag) or (None, None).
    """
    query = (
        "[out:json][timeout:25];"
        "("
          f"node(around:{radius},{lat},{lon})[amenity];"
          f"way(around:{radius},{lat},{lon})[amenity];"
          f"node(around:{radius},{lat},{lon})[shop];"
          f"way(around:{radius},{lat},{lon})[shop];"
          f"node(around:{radius},{lat},{lon})[office];"
          f"way(around:{radius},{lat},{lon})[office];"
        ");"
        "out tags center 1;"
    )
    resp = requests.post(OVERPASS_URL, data={"data": query})
    resp.raise_for_status()
    for elem in resp.json().get("elements", []):
        tags = elem.get("tags", {})
        name = tags.get("name")
        for key in ("amenity", "shop", "office"):
            if key in tags:
                return name, f"{key}={tags[key]}"
    return None, None

def reverse_nominatim(lat, lon):
    """
    Reverse-geocode (lat, lon) via Nominatim.
    Returns (display_name, osm_type, osm_id) or (None, None, None).
    """
    params = {
        "format": "jsonv2",
        "lat": lat,
        "lon": lon,
        "zoom": 18,
        "addressdetails": 0
    }
    headers = {"User-Agent": "osm-demo-script/1.0"}
    resp = requests.get(NOMINATIM_URL, params=params, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    return (
        data.get("display_name"),
        data.get("osm_type"),
        data.get("osm_id")
    )

def main():
    # 0) Load panel CSV and extract Functie
    panels = (
        pd.read_csv(PANEL_CSV, sep=";", dtype=str)
          .rename(columns={"OBJECTNUMMER": "Objectnummer"})
          [["Objectnummer", "Functie"]]
          .drop_duplicates("Objectnummer")
    )

    # 1) Load building CSV, force Objectnummer to string
    df = pd.read_csv(INPUT_CSV, dtype=str)
    df["latitude"] = df["latitude"].astype(float)
    df["longitude"] = df["longitude"].astype(float)

    # 2) Merge in Functie
    df = df.merge(panels, on="Objectnummer", how="left")

    # 3) Take a small test sample
    df = df.head(5)

    # 4) Prepare OSM columns
    df["OSM_BizName"] = ""
    df["OSM_BizTag"]  = ""
    df["OSM_Place"]   = ""
    df["OSM_Type"]    = ""
    df["OSM_ID"]      = ""

    # 5) Enrich each row
    for idx, row in df.iterrows():
        lat = row["latitude"]
        lon = row["longitude"]

        # Overpass business tags
        try:
            name, tag = fetch_osm_business(lat, lon)
        except Exception:
            name, tag = None, None

        # Nominatim reverse-geocode
        try:
            place, typ, oid = reverse_nominatim(lat, lon)
        except Exception:
            place, typ, oid = None, None, None

        df.at[idx, "OSM_BizName"] = name or ""
        df.at[idx, "OSM_BizTag"]  = tag  or ""
        df.at[idx, "OSM_Place"]   = place or ""
        df.at[idx, "OSM_Type"]    = typ   or ""
        df.at[idx, "OSM_ID"]      = oid   or ""

        time.sleep(PAUSE_S)

    # 6) Write out the test CSV
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"✅ Wrote {len(df)} rows to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
