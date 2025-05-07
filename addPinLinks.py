#!/usr/bin/env python3
"""
add_pin_links_final.py

Reads your final CSV (solar_buildings_final.csv), appends a
GoogleMapsPinURL column that drops a pin at each building’s
latitude/longitude, and writes out
solar_buildings_final_with_pin_links.csv.
"""

import pandas as pd
from pathlib import Path

# ───── Configuration ─────────────────────────────────────────────────────
INPUT_CSV  = Path("solar_buildings_final.csv")
OUTPUT_CSV = Path("solar_buildings_final_with_pin_links.csv")

def main():
    # 1) load the final CSV, ensuring lat/lon are floats
    df = pd.read_csv(INPUT_CSV, dtype={"latitude": float, "longitude": float})

    # 2) build pin URL for each row
    df["GoogleMapsPinURL"] = (
        "https://www.google.com/maps/search/?api=1&query="
        + df["latitude"].astype(str) + "," + df["longitude"].astype(str)
    )

    # 3) write out the new CSV
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"✅ Written {len(df)} rows to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
