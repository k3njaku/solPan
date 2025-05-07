#!/usr/bin/env python3
"""
add_googlemaps_url.py

Reads solar_buildings.csv, appends a GoogleMapsURL column for each
latitude/longitude, and writes out solar_buildings_with_url.csv.
"""

import pandas as pd
from pathlib import Path

INPUT_CSV  = Path("solar_buildings.csv")
OUTPUT_CSV = Path("solar_buildings_with_url.csv")

def main():
    df = pd.read_csv(INPUT_CSV, dtype={"latitude": float, "longitude": float})
    # Construct URL: Satellite view at zoom 19
    df["GoogleMapsURL"] = (
        "https://maps.google.com/?ll="
        + df["latitude"].astype(str)
        + ","
        + df["longitude"].astype(str)
        + "&t=k&z=19"
    )
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"✅ Written {len(df)} rows with URLs to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
