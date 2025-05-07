#!/usr/bin/env python3
"""
fix_google_links.py
Read final_output.csv, convert RD‑New coords to WGS‑84,
replace GoogleMaps column, and write final_output_wgs84.csv
"""

import csv
from pyproj import Transformer

INPUT  = "final_output.csv"
OUTPUT = "final_output_wgs84.csv"

xf = Transformer.from_crs("EPSG:28992", "EPSG:4326", always_xy=True)  # RD → WGS‑84

with open(INPUT, newline="", encoding="utf-8") as src, \
     open(OUTPUT, "w", newline="", encoding="utf-8") as dst:

    rdr = csv.DictReader(src)
    fieldnames = rdr.fieldnames
    wtr = csv.DictWriter(dst, fieldnames=fieldnames)
    wtr.writeheader()

    for row in rdr:
        try:
            rd_x  = float(row["Longitude"])
            rd_y  = float(row["Latitude"])
        except ValueError:
            continue              # skip bad numbers

        lon, lat = xf.transform(rd_x, rd_y)
        row["Longitude"]  = f"{lon:.6f}"
        row["Latitude"]   = f"{lat:.6f}"
        row["GoogleMaps"] = f"https://www.google.com/maps/search/?api=1&query={lat:.6f},{lon:.6f}"
        wtr.writerow(row)

print(f"✔ Updated file written to {OUTPUT}")
