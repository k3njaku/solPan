#!/usr/bin/env python3
"""
stage_bag_addresses.py

Phase 2 – Lookup BAG addresses for each panelled Objectnummer via PDOK Locatieserver Lookup.
"""

import csv
import logging
import requests

# ————— Configuration —————
LOC_LOOKUP = "https://api.pdok.nl/bzk/locatieserver/search/v3_1/lookup"
PANEL_CSV  = "panel_stage.csv"
OUTPUT_CSV = "bag_stage.csv"
# ——————————————————————————

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger()

def fetch_address(bag_id):
    """Lookup BAG address by ID; return dict or None."""
    params = {"id": bag_id}
    resp = requests.get(LOC_LOOKUP, params=params)
    resp.raise_for_status()
    docs = resp.json().get("response", {}).get("docs", [])
    if not docs:
        return None
    d = docs[0]
    return {
        "Objectnummer":    bag_id,
        "Street":          d.get("straatnaam"),
        "Housenumber":     d.get("huisnummer"),
        "PostalCode":      d.get("postcode"),
        "City":            d.get("woonplaatsnaam")
    }

def main():
    # 1) Read panel_stage.csv
    logger.info("Loading panel_stage.csv …")
    with open(PANEL_CSV, newline="", encoding="utf-8") as f:
        panel_ids = [row["Objectnummer"] for row in csv.DictReader(f)]

    # 2) Lookup each BAG ID
    out = []
    for pid in panel_ids:
        addr = fetch_address(pid)
        logger.info("Lookup %s → %s", pid, "found" if addr else "NOT found")
        if addr:
            out.append(addr)

    # 3) Write bag_stage.csv
    logger.info("Writing %s with %d records …", OUTPUT_CSV, len(out))
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "Objectnummer","Street","Housenumber","PostalCode","City"
        ])
        writer.writeheader()
        writer.writerows(out)
    logger.info("✔ Done")
    
if __name__ == "__main__":
    main()
