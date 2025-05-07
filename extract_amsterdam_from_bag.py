#!/usr/bin/env python3
"""
extract_amsterdam_local.py
------------------------------------------------------------
Reads your local BAG GeoPackage ('bag-light.gpkg') and CBS
municipality boundaries ('wijkenbuurten_2024_v1.gpkg'),
keeps only buildings inside Amsterdam (CBS code GM0363),
and writes bag_amsterdam.gpkg.

No downloads, 100 % offline.

USAGE
-----
python extract_amsterdam_local.py
"""

import logging
from pathlib import Path

import fiona
import geopandas as gpd
from shapely.geometry import box
from tqdm import tqdm

# ------------------------------------------------------------------#
# File paths — match what you showed in the screenshot
# ------------------------------------------------------------------#
BAG_PATH  = Path("bag-light.gpkg")
CBS_PATH  = Path("wijkenbuurten_2024_v1.gpkg")
OUT_FILE  = Path("bag_amsterdam.gpkg")
MUNICODE  = "GM0363"           # Amsterdam

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")

# ------------------------------------------------------------------#
# Helper functions
# ------------------------------------------------------------------#
def find_layer(path: Path, token: str):
    """Return first layer name that contains *token* (case‑insensitive)."""
    for lyr in fiona.listlayers(path):
        if token.lower() in lyr.lower():
            return lyr
    raise RuntimeError(f"No layer containing '{token}' found in {path}")

def detect_code_column(df: gpd.GeoDataFrame, muni_code: str):
    """Return the column name that contains the municipality code."""
    for col in df.columns:
        if df[col].astype(str).str.contains(muni_code).any():
            return col
    raise RuntimeError(f"No column with value '{muni_code}' found in municipality layer")

# ------------------------------------------------------------------#
# Main workflow
# ------------------------------------------------------------------#
def main():
    # 1️⃣  Load Amsterdam polygon from CBS municipalities
    muni_layer = find_layer(CBS_PATH, "gemeente")
    logging.info("Municipality layer detected: %s", muni_layer)
    muni = gpd.read_file(CBS_PATH, layer=muni_layer)

    code_col = detect_code_column(muni, MUNICODE)
    logging.info("Municipality‑code column detected: %s", code_col)

    ams_poly = muni.loc[muni[code_col] == MUNICODE, "geometry"].values[0]
    bbox = box(*ams_poly.bounds)
    logging.info("Amsterdam bbox = %s", tuple(round(c, 4) for c in bbox.bounds))

    # 2️⃣  Load BAG ‘pand’ layer within that bbox
    pand_layer = find_layer(BAG_PATH, "pand")
    logging.info("BAG layer detected: %s", pand_layer)
    with tqdm(total=1, desc="Loading BAG subset", unit="step"):
        pand = gpd.read_file(BAG_PATH, layer=pand_layer, bbox=bbox)
        pand = pand[pand.geometry.intersects(ams_poly)].copy()

    logging.info("Rows after precise clip: %d", len(pand))

    # 3️⃣  Save result
    if OUT_FILE.exists():
        OUT_FILE.unlink()
    pand.to_file(OUT_FILE, layer="pand", driver="GPKG")
    logging.info("Saved %s (%d rows, %d columns)",
                 OUT_FILE, len(pand), pand.shape[1])

if __name__ == "__main__":
    main()
