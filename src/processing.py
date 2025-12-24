"""
processing.py

Data processing and harmonization logic for the climate scenario analysis pipeline.

This module transforms raw OWID and IEA datasets into a single canonical,
long-format dataset with a standardized schema.

All assumptions, filters, and transformations are made explicit to ensure
transparency, reproducibility, and academic defensibility.
"""

import pandas as pd

from src.config import (
    WORLD_REGION_NAME,
    HISTORICAL_START_YEAR,
    HISTORICAL_END_YEAR,
    SCENARIO_END_YEAR,
    EMISSIONS_UNIT,
    CO2_VARIABLE_NAME,
    CANONICAL_COLUMNS,
    IEA_CO2_CATEGORY,
    IEA_CO2_PRODUCT,
    IEA_CO2_UNIT_RAW,
    IEA_ALLOWED_FLOWS,
)


def process_owid_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process the raw OWID dataset and convert it into the canonical schema.

    Steps:
    - Restrict to global (World) data
    - Restrict to historical years
    - Select total CO2 emissions
    - Rename and enrich columns to match the canonical schema
    - Enforce historical sanity checks (no negative emissions)

    Parameters
    ----------
    df : pd.DataFrame
        Raw OWID dataset.

    Returns
    -------
    pd.DataFrame
        Canonical-formatted OWID historical emissions data.
    """
    # -----------------------------
    # Filter to global-level data
    # -----------------------------
    df = df[df["country"] == WORLD_REGION_NAME].copy()

    # -----------------------------
    # Restrict to historical period
    # -----------------------------
    df = df[
        (df["year"] >= HISTORICAL_START_YEAR) &
        (df["year"] <= HISTORICAL_END_YEAR)
    ].copy()

    # -----------------------------
    # Select relevant variable
    # -----------------------------
    # We explicitly use total CO2 emissions (energy-related),
    # excluding land-use change and other GHGs.
    df = df[["year", "co2"]].copy()

    # -----------------------------
    # Rename and enrich to canonical schema
    # -----------------------------
    df.rename(columns={"co2": "value"}, inplace=True)

    df["region"] = WORLD_REGION_NAME
    # Align with IEA "total" series flow naming so we can anchor scenarios to history.
    df["sector"] = "Total energy supply"
    df["scenario"] = "historical"
    df["variable"] = CO2_VARIABLE_NAME
    df["unit"] = EMISSIONS_UNIT
    df["source"] = "OWID"

    # -----------------------------
    # Drop rows with missing values explicitly
    # -----------------------------
    df = df.dropna(subset=["value"])

    # -----------------------------
    # Sanity check: historical emissions must be non-negative
    # -----------------------------
    assert (df["value"] >= 0).all(), (
        "Negative historical emissions detected in OWID data."
    )

    # -----------------------------
    # Enforce canonical column order
    # -----------------------------
    df = df[CANONICAL_COLUMNS]

    return df


def process_iea_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process the raw IEA Annex A dataset and convert it into the canonical schema.

    Steps (strict, to avoid double counting):
    - Restrict to global (World) data
    - Normalize scenario names to canonical labels (STEPS, NZE)
    - Select ONE defensible emissions series definition:
        - CATEGORY == 'CO2 total'
        - PRODUCT == 'Total'
        - UNIT == 'Mt CO2'
        - FLOW in a controlled allow-list (top-level flows only)
    - Restrict to scenario time horizon
    - Rename and enrich columns to match the canonical schema

    Notes
    -----
    Negative emissions values are explicitly allowed here, as IEA Net Zero
    scenarios model carbon removal technologies such as BECCS and DAC.

    Parameters
    ----------
    df : pd.DataFrame
        Raw IEA Annex A dataset.

    Returns
    -------
    pd.DataFrame
        Canonical-formatted IEA scenario emissions data.
    """
    # -----------------------------
    # Filter to global-level data
    # -----------------------------
    df = df[df["REGION"] == WORLD_REGION_NAME].copy()

    # -----------------------------
    # Normalize scenario names
    # -----------------------------
    # IEA scenario labels vary across publications; we explicitly map them
    # to canonical short names to ensure robust downstream analysis.
    scenario_mapping = {
        "stated policies": "STEPS",
        "steps": "STEPS",
        "net zero": "NZE",
        "nze": "NZE",
    }

    def map_scenario(name: str) -> str | None:
        if not isinstance(name, str):
            return None
        name_lower = name.lower()
        for key, value in scenario_mapping.items():
            if key in name_lower:
                return value
        return None

    df["scenario"] = df["SCENARIO"].apply(map_scenario)

    # Keep only scenarios we explicitly analyze
    df = df[df["scenario"].notna()].copy()

    # -----------------------------
    # Restrict to a single CO2 series definition (avoid double counting)
    # -----------------------------
    required_cols = {"CATEGORY", "PRODUCT", "FLOW", "UNIT"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"IEA raw data missing required columns: {sorted(missing)}")

    df = df[
        (df["CATEGORY"] == IEA_CO2_CATEGORY)
        & (df["PRODUCT"] == IEA_CO2_PRODUCT)
        & (df["UNIT"] == IEA_CO2_UNIT_RAW)
        & (df["FLOW"].isin(IEA_ALLOWED_FLOWS))
    ].copy()

    # Hard fail if empty: prevents silently producing nonsense downstream.
    if df.empty:
        raise ValueError(
            "IEA CO2 selection returned 0 rows. Check config IEA_CO2_* constants "
            "and the raw dataset schema."
        )

    # -----------------------------
    # Restrict to scenario projection years
    # -----------------------------
    df = df[df["YEAR"] <= SCENARIO_END_YEAR].copy()

    # -----------------------------
    # Rename columns to canonical names
    # -----------------------------
    df.rename(
        columns={
            "YEAR": "year",
            "REGION": "region",
            "VALUE": "value",
            "UNIT": "unit",
        },
        inplace=True,
    )

    # -----------------------------
    # Enrich with canonical fields
    # -----------------------------
    # Use FLOW as our sector dimension (top-level, allow-listed)
    df["sector"] = df["FLOW"].astype(str)
    df["variable"] = CO2_VARIABLE_NAME
    df["source"] = "IEA_WEO_2025"
    # Standardize unit string to canonical convention (MtCO2)
    df["unit"] = EMISSIONS_UNIT

    # -----------------------------
    # Drop rows with missing values explicitly
    # -----------------------------
    df = df.dropna(subset=["value"])

    # -----------------------------
    # Uniqueness checks: exactly one value per (year, scenario, sector)
    # -----------------------------
    dup_counts = (
        df.groupby(["year", "scenario", "sector"], as_index=False)
        .size()
        .rename(columns={"size": "n"})
    )
    if (dup_counts["n"] > 1).any():
        raise ValueError(
            "IEA CO2 selection is not unique per (year, scenario, sector). "
            "This indicates potential double counting or an overly broad selector."
        )

    # -----------------------------
    # Enforce canonical column order
    # -----------------------------
    df = df[CANONICAL_COLUMNS]

    return df


def build_canonical_dataset(
    owid_df: pd.DataFrame,
    iea_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Combine processed OWID and IEA datasets into a single canonical dataset.

    Parameters
    ----------
    owid_df : pd.DataFrame
        Processed OWID historical emissions data.
    iea_df : pd.DataFrame
        Processed IEA scenario emissions data.

    Returns
    -------
    pd.DataFrame
        Unified canonical dataset containing historical and scenario data.
    """
    # -----------------------------
    # Concatenate datasets
    # -----------------------------
    combined_df = pd.concat([owid_df, iea_df], ignore_index=True)

    # -----------------------------
    # Schema validation
    # -----------------------------
    assert set(combined_df.columns) == set(CANONICAL_COLUMNS), (
        "Canonical dataset does not match expected schema."
    )

    return combined_df