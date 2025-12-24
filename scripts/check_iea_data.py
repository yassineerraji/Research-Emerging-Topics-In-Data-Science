"""
Lightweight helper to validate that the required IEA file is present.

Usage:
    python scripts/check_iea_data.py
"""

from src.config import IEA_ANNEX_FILE


def main() -> None:
    if IEA_ANNEX_FILE.exists():
        print(f"[INFO] IEA Annex file found: {IEA_ANNEX_FILE}")
    else:
        raise FileNotFoundError(
            f"IEA Annex file not found at {IEA_ANNEX_FILE}. "
            "Place 'WEO2025_AnnexA_Free_Dataset_World.csv' into data/raw/."
        )


if __name__ == "__main__":
    main()


