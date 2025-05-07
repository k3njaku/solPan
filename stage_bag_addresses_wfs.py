#!/usr/bin/env python3
"""
stage_bag_addresses_wfs.py

Phase 2 – Batch‐fetch BAG address info for panelled Objectnummer via BAG WFS v2.0,
using small batches to keep the URL short.
"""

import csv, logging, requests
from itertools import islice

# ————— Configuration —————
PANEL_CSV  = "panel_stage.csv"
OUTPUT_CSV = "bag_stage.csv"
WFS_URL    = "https://service.pdok.nl/lv/bag/wfs/v2_0"
BATCH_SIZE = 50    # small enough that the URL stays under header limits
# ——————————————————————————

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger()

def chunked(iterable, size):
    it = iter(iterable)
    while True:
        batch = list(islice(it, size))
        if not batch:
            return
        yield batch

def fetch_addresses(batch_ids):
    """Fetch BAG verblijfsobject for a list of pand IDs (up to BATCH_SIZE)."""
    # build a CQL IN list: 'id1','id2',...
    quoted = ",".join(f"'{pid}'" for pid in batch_ids)
    params = {
        "service":      "WFS",
        "version":      "2.0.0",
        "request":      "GetFeature",
        "typeNames":    "bag:verblijfsobject",
        "outputFormat": "application/json",
        "CQL_FILTER":   f"pand_identificatie IN ({quoted})"
    }
    logger.info(f"Fetching {len(batch_ids)} addresses via WFS…")
    resp = requests.get(WFS_URL, params=params, timeout=60)
    resp.raise_for_status()
    features = resp.json().get("features", [])
    out = {}
    for feat in features:
        p = feat["properties"]
        pid = p.get("pand_identificatie") or p.get("pandIdentificatie")
        if not pid:
            continue
        out[pid] = {
            "Street":      p.get("openbare_ruimte_naam") or p.get("openbareRuimteNaam"),
            "Housenumber": p.get("huisnummer"),
            "PostalCode":  p.get("postcode"),
            "City":        p.get("woonplaats_naam") or p.get("woonplaatsNaam")
        }
    return out

def main():
    logger.info("Loading panel_stage.csv …")
    with open(PANEL_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        panel_ids = [row["Objectnummer"] for row in reader]

    address_index = {}
    for batch in chunked(panel_ids, BATCH_SIZE):
        fetched = fetch_addresses(batch)
        address_index.update(fetched)

    logger.info(f"Total addresses fetched: {len(address_index)}")

    logger.info("Writing %s …", OUTPUT_CSV)
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Objectnummer","Street","Housenumber","PostalCode","City"])
        for pid in panel_ids:
            addr = address_index.get(pid)
            if not addr:
                continue
            writer.writerow([pid, addr["Street"], addr["Housenumber"],
                             addr["PostalCode"], addr["City"]])
    logger.info("✔ Done writing %s", OUTPUT_CSV)

if __name__ == "__main__":
    main()
