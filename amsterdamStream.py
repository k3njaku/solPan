#!/usr/bin/env python3
import fiona
import csv
from shapely.geometry import shape
from pyproj import Transformer

# 1. Transformer: RD New (EPSG:28992) → WGS84 (EPSG:4326)
transformer = Transformer.from_crs("EPSG:28992", "EPSG:4326", always_xy=True)

# 2. File & layer names
GPKG_PATH = "bag-light.gpkg"
LAYER_NAME = "verblijfsobject"
OUTPUT_CSV = "amsterdam_addresses.csv"

# 3. Open the GeoPackage layer and the CSV writer
with fiona.open(GPKG_PATH, layer=LAYER_NAME) as src, \
     open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as fout:

    # Define your final columns/order
    writer = csv.DictWriter(fout, fieldnames=[
        "identificatie",
        "woningtype",
        "straat",
        "huisnummer",
        "huisletter",
        "toevoeging",
        "postcode",
        "woonplaats",
        "lon",
        "lat",
        "google_maps_link"
    ])
    writer.writeheader()

    # 4. Stream through each address-point
    for feat in src:
        p = feat["properties"]

        # 4a. Keep only Amsterdam rows
        if p.get("woonplaats_naam", "").lower() != "amsterdam":
            continue

        # 4b. Build lon/lat from the geometry
        geom = shape(feat["geometry"])
        lon, lat = transformer.transform(geom.x, geom.y)

        # 4c. Write out the row
        writer.writerow({
            "identificatie":      p.get("identificatie", ""),
            "woningtype":         p.get("gebruiksdoel", ""),
            "straat":             p.get("openbare_ruimte_naam", ""),
            "huisnummer":         p.get("huisnummer", ""),
            "huisletter":         p.get("huisletter", ""),
            "toevoeging":         p.get("toevoeging", ""),
            "postcode":           p.get("postcode", ""),
            "woonplaats":         p.get("woonplaats_naam", ""),
            "lon":                round(lon, 6),
            "lat":                round(lat, 6),
            "google_maps_link":   f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
        })

print(f"✅ Wrote Amsterdam addresses to {OUTPUT_CSV}")
