"""
io.py

Input/output utilities for loading raw climate datasets.

This module is responsible ONLY for:
- loading raw data files from disk
- performing minimal validation (e.g., file existence)

It must NOT:
- clean data
- filter rows
- rename columns
- modify units

All transformations belong in processing.py.
"""

import pandas as pd

from src.config import OWID_CO2_FILE, IEA_ANNEX_FILE


def load_owid_raw() -> pd.DataFrame:
    """
    Load the raw OWID CO2 dataset from disk.

    Returns
    -------
    pd.DataFrame
        Raw OWID dataset as loaded from the CSV file.

    Raises
    ------
    FileNotFoundError
        If the OWID data file is not found at the expected path.
    """
    if not OWID_CO2_FILE.exists():
        raise FileNotFoundError(
            f"OWID CO2 data file not found at {OWID_CO2_FILE}"
        )

    # Load CSV exactly as provided by OWID
    df = pd.read_csv(OWID_CO2_FILE)

    return df


def load_iea_annex() -> pd.DataFrame:
    """
    Load the raw IEA World Energy Outlook Annex A dataset from disk.

    Returns
    -------
    pd.DataFrame
        Raw IEA Annex A dataset as loaded from the CSV file.

    Raises
    ------
    FileNotFoundError
        If the IEA Annex A data file is not found at the expected path.
    """
    if not IEA_ANNEX_FILE.exists():
        raise FileNotFoundError(
            f"IEA Annex A data file not found at {IEA_ANNEX_FILE}"
        )

    # Load CSV exactly as provided by the IEA
    df = pd.read_csv(IEA_ANNEX_FILE)

    return df