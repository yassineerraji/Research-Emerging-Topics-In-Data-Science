"""
Download the latest OWID CO2 dataset into data/raw/.

Usage:
    python scripts/update_owid.py

Note:
    This requires network access. In some course environments, network may be blocked;
    in that case, place the file manually into data/raw/owid-co2-data.csv.
"""

from __future__ import annotations

import urllib.request
from pathlib import Path

from src.config import OWID_CO2_FILE

# OWID publishes a stable CSV endpoint for the CO2 dataset.
OWID_CO2_URL = "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv"


def main() -> None:
    OWID_CO2_FILE.parent.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] Downloading OWID CO2 dataset from: {OWID_CO2_URL}")
    print(f"[INFO] Saving to: {OWID_CO2_FILE}")
    urllib.request.urlretrieve(OWID_CO2_URL, OWID_CO2_FILE)  # nosec: educational project
    print("[INFO] Download complete.")


if __name__ == "__main__":
    main()


