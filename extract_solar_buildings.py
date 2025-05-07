#!/usr/bin/env python3
"""
extract_solar_buildings_preview.py

Spatially join your panel-point CSV to Amsterdam BAG buildings,
enrich with address info, then export just the first 100 rows for review.
"""

import logging
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

# ───── Config ─────────────────────────────────────────────────────────────
BAG_AMS    = Path("bag_amsterdam.gpkg")
BAG_FULL   = Path("bag-light.gpkg")
PANELS_CSV = Path("ZONNEPANELEN.csv")
OUT_CSV    = Path("solar_buildings_preview.csv")

BUILD_LYR  = "pand"
ADDR_LYR   = "verblijfsobject"

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")


def main():
    # 1️⃣ Load Amsterdam building footprints
    gdf_build = gpd.read_file(BAG_AMS, layer=BUILD_LYR)
    crs = gdf_build.crs

    # 2️⃣ Load panel CSV → points in BAG CRS
    df_pan = pd.read_csv(PANELS_CSV, sep=";").dropna(subset=["LNG","LAT"])
    df_pan[["LNG","LAT"]] = df_pan[["LNG","LAT"]].astype(float)
    gdf_pan = gpd.GeoDataFrame(
        df_pan,
        geometry=[Point(xy) for xy in zip(df_pan.LNG, df_pan.LAT)],
        crs="EPSG:4326"
    ).to_crs(crs)

    # 3️⃣ Spatial join → which buildings contain panels
    joined = gpd.sjoin(
        gdf_build[["identificatie","geometry"]],
        gdf_pan[["geometry"]],
        predicate="contains",
        how="inner"
    )
    ids = joined.identificatie.unique().tolist()

    # 4️⃣ Read only address records in Amsterdam bbox
    minx, miny, maxx, maxy = gdf_build.total_bounds
    gdf_addr = gpd.read_file(
        BAG_FULL,
        layer=ADDR_LYR,
        bbox=(minx, miny, maxx, maxy)
    )

    # 5️⃣ Detect the right pand-ID column
    pand_col = next(
        c for c in gdf_addr.columns
        if "pand" in c.lower() and "identificatie" in c.lower()
    )

    # 6️⃣ Filter only our panelled buildings
    gdf_addr = gdf_addr[gdf_addr[pand_col].isin(ids)]

    # 7️⃣ Merge address ↔ building footprints (to pull gebruiksdoel & geometry)
    df = pd.merge(
        gdf_addr.to_crs(epsg=4326),
        gdf_build.to_crs(epsg=4326)[["identificatie","gebruiksdoel","geometry"]],
        left_on=pand_col,
        right_on="identificatie",
        suffixes=("_addr","_bld")
    )

    # 8️⃣ Compute centroids & URLs
    df["longitude"] = df.geometry_bld.centroid.x
    df["latitude"]  = df.geometry_bld.centroid.y
    df["GoogleMapsURL"] = (
        "https://www.google.com/maps/search/?api=1&query="
        + df.latitude.astype(str) + "," + df.longitude.astype(str)
    )

    # 9️⃣ Select, rename & limit to 100 rows
    preview = (
        df[[
            "identificatie",           # Objectnummer
            "openbare_ruimte_naam",    # Street
            "huisnummer",              # Housenumber
            "postcode",                # Postal code
            "woonplaats_naam",         # City
            "gebruiksdoel",            # Gebruiksdoel
            "functie",                 # Functie (if present)
            "GoogleMapsURL","longitude","latitude"
        ]]
        .rename(columns={
            "identificatie":"Objectnummer",
            "openbare_ruimte_naam":"Street",
            "huisnummer":"Housenumber",
            "postcode":"Postal code",
            "woonplaats_naam":"City",
            "gebruiksdoel":"Gebruiksdoel",
            "functie":"Functie"
        })
        .assign(Country="NL")
        .head(100)
    )

    # 🔟 Write preview CSV
    preview.to_csv(OUT_CSV, index=False)
    logging.info("Wrote %d preview rows to %s", len(preview), OUT_CSV)


if __name__ == "__main__":
    main()
