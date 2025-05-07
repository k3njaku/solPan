#!/usr/bin/env python3
"""
One-shot download of CBS StatLine dataset 85140NED (dwellings with/without PV)
– full CSV export (or filtered to Haarlem)
"""

import logging
import requests

# ── Logging configuration ──────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

# ── Configuration ──────────────────────────────────────────────────────────────
BASE_URL   = "https://datasets.cbs.nl/odata/v1/CBS/85140NED/Observations"
# To download only Haarlem, uncomment the next line
# REGION     = "GM0392"
OUT_FILE   = "haarlem_full.csv"  # adjust if you fetch the entire table

# ── Build request parameters ───────────────────────────────────────────────────
params = {
    "$format": "csv"            # full CSV export
}
# if you want **only** Haarlem, uncomment:
# params["$filter"] = f"RegioS eq '{REGION}'"

# ── Execute streaming download ────────────────────────────────────────────────
logging.info("Requesting full CSV export from CBS OData API")
try:
    with requests.get(BASE_URL, params=params, stream=True, timeout=60) as resp:
        resp.raise_for_status()

        with open(OUT_FILE, "wb") as f:
            for chunk in resp.iter_content(chunk_size=16_384):
                if chunk:
                    f.write(chunk)

    logging.info("Saved data to %s", OUT_FILE)

except Exception as e:
    logging.error("Download failed: %s", e)
    raise
