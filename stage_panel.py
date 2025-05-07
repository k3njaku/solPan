#!/usr/bin/env python3
"""
stage_panel_local.py

Phase 1 – Read the local zonnepanelen2022.json and stage into CSV:
  Objectnummer,PanelCount,Longitude,Latitude
"""

import json
import csv
import logging

# ————— Configuration —————
INPUT_JSON = "zonnepanelen2022.json"
OUTPUT_CSV = "panel_stage.csv"
# ——————————————————————————

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger()

def main():
    # Load the GeoJSON-like structure
    logger.info("Loading %s …", INPUT_JSON)
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    features = data.get("features", [])
    logger.info("Found %d features", len(features))

    # Write CSV
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Objectnummer", "PanelCount", "Longitude", "Latitude"])
        for feat in features:
            props = feat.get("properties", {})
            coords = feat.get("geometry", {}).get("coordinates", [])
            # field mappings based on sample output
            obj = props.get("identifica") or props.get("identificatie")
            cnt = props.get("aantal")
            # pull the first vertex of the outer ring
            try:
                lon, lat = coords[0][0]
            except Exception:
                continue
            if not obj or cnt is None:
                continue
            writer.writerow([obj, cnt, lon, lat])

    logger.info("✔ Staged %d rows to %s", len(features), OUTPUT_CSV)

if __name__ == "__main__":
    main()
