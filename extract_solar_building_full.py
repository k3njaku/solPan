#!/usr/bin/env python3
"""
extract_solar_buildings_full.py

Full export of Amsterdam buildings with solar panels.
Fields: Objectnummer, Street, Housenumber, Postal code,
City, Country, Gebruiksdoel, longitude, latitude.
Excludes GoogleMapsURL and functie.
"""

import logging
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

# ───── Configuration ─────────────────────────────────────────────────────
BAG_AMS    = Path("bag_amsterdam.gpkg")    # your Amsterdam footprints
BAG_FULL   = Path("bag-light.gpkg")        # full national BAG GeoPackage
PANELS_CSV = Path("ZONNEPANELEN.csv")      # panel-point CSV
OUT_CSV    = Path("solar_buildings.csv")   # output CSV

BUILD_LYR  = "pand"
ADDR_LYR   = "verblijfsobject"

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")


def main():
    # 1️⃣ Load Amsterdam building footprints
    logging.info("Loading BAG Amsterdam footprints…")
    gdf_build = gpd.read_file(BAG_AMS, layer=BUILD_LYR)
    build_crs = gdf_build.crs
    logging.info("  %d buildings loaded", len(gdf_build))

    # 2️⃣ Load panel CSV → points in BAG CRS
    logging.info("Loading panel points…")
    df_pan = pd.read_csv(PANELS_CSV, sep=";").dropna(subset=["LNG","LAT"])
    df_pan["LNG"] = df_pan["LNG"].astype(float)
    df_pan["LAT"] = df_pan["LAT"].astype(float)
    gdf_pan = gpd.GeoDataFrame(
        df_pan,
        geometry=[Point(xy) for xy in zip(df_pan.LNG, df_pan.LAT)],
        crs="EPSG:4326"
    ).to_crs(build_crs)
    logging.info("  %d panel points", len(gdf_pan))

    # 3️⃣ Spatial join → find buildings containing panels
    logging.info("Spatial join to find buildings with panels…")
    joined = gpd.sjoin(
        gdf_build[["identificatie","geometry"]],
        gdf_pan[["geometry"]],
        predicate="contains",
        how="inner"
    )
    panelled_ids = joined.identificatie.unique().tolist()
    logging.info("  %d buildings contain panels", len(panelled_ids))

    # 4️⃣ Load only address records within Amsterdam bbox
    minx, miny, maxx, maxy = gdf_build.total_bounds
    logging.info("Loading address records within bbox…")
    gdf_addr = gpd.read_file(
        BAG_FULL,
        layer=ADDR_LYR,
        bbox=(minx, miny, maxx, maxy)
    )
    logging.info("  %d address records loaded", len(gdf_addr))

    # 5️⃣ Detect the correct pand-ID column
    key = next(c for c in gdf_addr.columns
               if "pand" in c.lower() and "identificatie" in c.lower())
    logging.info("Address key column: %s", key)

    # 6️⃣ Filter address records to panelled buildings
    gdf_addr = gdf_addr[gdf_addr[key].isin(panelled_ids)]
    logging.info("  %d address records for panelled buildings", len(gdf_addr))

    # 7️⃣ Merge address ↔ building usage & geometry
    logging.info("Merging address and building data…")
    df_full = pd.merge(
        gdf_addr.to_crs(epsg=4326)[[key,
            "openbare_ruimte_naam","huisnummer",
            "postcode","woonplaats_naam"
        ]].rename(columns={key: "identificatie"}),
        gdf_build.to_crs(epsg=4326)[["identificatie","gebruiksdoel","geometry"]],
        on="identificatie",
        how="inner"
    )
    logging.info("  %d merged records", len(df_full))

    # 8️⃣ Compute centroids via apply (plain DataFrame)
    logging.info("Computing centroids…")
    df_full["longitude"] = df_full.geometry.apply(lambda g: g.centroid.x)
    df_full["latitude"]  = df_full.geometry.apply(lambda g: g.centroid.y)

    # 9️⃣ Select, rename, add Country
    out = df_full[[
        "identificatie",
        "openbare_ruimte_naam","huisnummer",
        "postcode","woonplaats_naam",
        "gebruiksdoel","longitude","latitude"
    ]].rename(columns={
        "identificatie":           "Objectnummer",
        "openbare_ruimte_naam":    "Street",
        "huisnummer":              "Housenumber",
        "postcode":                "Postal code",
        "woonplaats_naam":         "City",
        "gebruiksdoel":            "Gebruiksdoel"
    })
    out["Country"] = "NL"
    cols = [
        "Objectnummer","Street","Housenumber",
        "Postal code","City","Country",
        "Gebruiksdoel","longitude","latitude"
    ]
    out = out[cols]

    # 🔟 Write CSV
    logging.info("Writing %s …", OUT_CSV)
    out.to_csv(OUT_CSV, index=False)
    logging.info("Done: %d rows", len(out))


if __name__ == "__main__":
    main()
