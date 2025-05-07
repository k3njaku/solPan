#!/usr/bin/env python3
"""
extract_amsterdam_local.py
------------------------------------------------------------
Reads your local BAG GeoPackage ('bag-light.gpkg') and CBS
municipality boundaries ('wijkenbuurten_2024_v1.gpkg'),
keeps only buildings inside Amsterdam (CBS code GM0363),
and writes bag_amsterdam.gpkg.

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
# Configuration – filenames from your screenshot
# ------------------------------------------------------------------#
BAG_PATH  = Path("bag-light.gpkg")
CBS_PATH  = Path("wijkenbuurten_2024_v1.gpkg")
OUT_FILE  = Path("bag_amsterdam.gpkg")
MUNICODE  = "GM0363"           # Amsterdam

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")

def find_layer(path: Path, token: str):
    """Return first layer name that contains token (case‑insensitive)."""
    for lyr in fiona.listlayers(path):
        if token.lower() in lyr.lower():
            return lyr
    raise RuntimeError(f"No layer containing '{token}' found in {path}")

def main():
    # 1️⃣  Load Amsterdam polygon from CBS municipalities
    muni_layer = find_layer(CBS_PATH, "gemeente")
    logging.info("Municipality layer detected: %s", muni_layer)
    muni = gpd.read_file(CBS_PATH, layer=muni_layer)
    ams_poly = muni.loc[muni["statcode"] == MUNICODE, "geometry"].values[0]
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
