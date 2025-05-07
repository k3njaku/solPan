#!/usr/bin/env python3
"""
extract_amsterdam_checked.py
-----------------------------------------------
Offline clip of Amsterdam (GM0363) from your local BAG file.

• Uses 'bag-light.gpkg' for BAG buildings
• Uses 'wijkenbuurten_2024_v1.gpkg' for municipality boundaries
• Auto-detects layer names, CRS, and code column
• Merges all parts of the municipality before clipping
• Logs counts after bbox filter and precise clip
• Writes 'bag_amsterdam.gpkg' (~190 000 rows)
"""

import logging
from pathlib import Path

import fiona
import geopandas as gpd
from pyproj import CRS
from shapely.geometry import box
from shapely.ops import unary_union
from tqdm import tqdm

# ───── Configuration ─────────────────────────────────────────────────────
BAG_PATH  = Path("bag-light.gpkg")
CBS_PATH  = Path("wijkenbuurten_2024_v1.gpkg")
OUT_FILE  = Path("bag_amsterdam.gpkg")
MUNICODE  = "GM0363"   # Amsterdam CBS code

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ───── Helpers ────────────────────────────────────────────────────────────
def first_layer(path: Path, token: str) -> str:
    for lyr in fiona.listlayers(path):
        if token.lower() in lyr.lower():
            return lyr
    raise RuntimeError(f"No layer containing '{token}' in {path}")

def detect_code_column(df: gpd.GeoDataFrame, code: str) -> str:
    for col in df.columns:
        if df[col].astype(str).eq(code).any():
            return col
    raise RuntimeError(f"No column with exact value '{code}' in municipality layer")

def read_crs(path: Path, layer: str) -> CRS:
    with fiona.open(path, layer=layer) as src:
        # prefer WKT if available
        return CRS.from_user_input(src.crs or src.crs_wkt)

# ───── Main ───────────────────────────────────────────────────────────────
def main():
    # 1️⃣  Load CBS “gemeenten” layer and merge all parts for GM0363
    muni_layer = first_layer(CBS_PATH, "gemeente")
    logging.info("Municipality layer: %s", muni_layer)
    muni_crs = read_crs(CBS_PATH, muni_layer)
    muni = gpd.read_file(CBS_PATH, layer=muni_layer)

    code_col = detect_code_column(muni, MUNICODE)
    logging.info("Municipality code column: %s", code_col)

    parts = muni.loc[muni[code_col] == MUNICODE, "geometry"]
    ams_poly_rd = unary_union(parts)   # merge all fragments

    # 2️⃣  Detect BAG layer & its CRS
    pand_layer = first_layer(BAG_PATH, "pand")
    bag_crs    = read_crs(BAG_PATH, pand_layer)
    logging.info("BAG layer: %s (CRS %s)", pand_layer, bag_crs.to_string())

    # 3️⃣  Project the merged Amsterdam shape into BAG CRS, build bbox
    ams_poly_bag = (
        gpd.GeoSeries([ams_poly_rd], crs=muni_crs)
           .to_crs(bag_crs)
           .iloc[0]
    )
    bbox = box(*ams_poly_bag.bounds)
    logging.info(
        "Amsterdam bbox in BAG CRS: %s",
        ", ".join(f"{c:.2f}" for c in bbox.bounds)
    )

    # 4️⃣  Read BAG subset with bbox filter, then precise clip
    logging.info("Loading BAG subset within bbox…")
    with tqdm(desc="Loading bbox subset", unit="batch"):
        pand_all = gpd.read_file(
            BAG_PATH,
            layer=pand_layer,
            bbox=bbox
        )
    logging.info("Rows after bbox filter: %d", len(pand_all))

    pand_clip = pand_all[pand_all.geometry.intersects(ams_poly_bag)].copy()
    logging.info("Rows after precise clip: %d", len(pand_clip))

    if pand_clip.empty:
        raise RuntimeError("Clip returned zero rows—something’s still off")

    # 5️⃣  Save result
    OUT_FILE.unlink(missing_ok=True)
    pand_clip.to_file(OUT_FILE, layer="pand", driver="GPKG")
    logging.info(
        "Saved %s (%d rows, %d columns)",
        OUT_FILE, len(pand_clip), pand_clip.shape[1]
    )

if __name__ == "__main__":
    main()
