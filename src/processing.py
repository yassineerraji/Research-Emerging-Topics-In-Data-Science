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
)


def process_owid_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process the raw OWID dataset and convert it into the canonical schema.

    Steps:
    - Restrict to global (World) data
    - Restrict to historical years
    - Select total CO2 emissions
    - Rename and enrich columns to match the canonical schema

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
    df["sector"] = "All"
    df["scenario"] = "historical"
    df["variable"] = CO2_VARIABLE_NAME
    df["unit"] = EMISSIONS_UNIT
    df["source"] = "OWID"

    # -----------------------------
    # Drop rows with missing values explicitly
    # -----------------------------
    df = df.dropna(subset=["value"])

    # -----------------------------
    # Enforce canonical column order
    # -----------------------------
    df = df[CANONICAL_COLUMNS]

    return df


def process_iea_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process the raw IEA Annex A dataset and convert it into the canonical schema.

    Steps:
    - Restrict to global (World) data
    - Restrict to CO2 emissions variables
    - Restrict to scenario time horizon
    - Rename and enrich columns to match the canonical schema

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
    # Restrict to CO2 emissions variables
    # -----------------------------
    # We keep rows where the category explicitly refers to CO2 emissions.
    # This avoids ambiguity with energy flows or non-CO2 gases.
    df = df[df["CATEGORY"].str.contains("CO2", case=False, na=False)].copy()

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
            "SCENARIO": "scenario",
            "VALUE": "value",
            "UNIT": "unit",
        },
        inplace=True,
    )

    # -----------------------------
    # Enrich with canonical fields
    # -----------------------------
    df["sector"] = "All"
    df["variable"] = CO2_VARIABLE_NAME
    df["source"] = "IEA_WEO_2025"

    # -----------------------------
    # Drop rows with missing values explicitly
    # -----------------------------
    df = df.dropna(subset=["value"])

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
    # Basic sanity checks
    # -----------------------------
    # Ensure canonical columns are present
    assert set(combined_df.columns) == set(CANONICAL_COLUMNS), (
        "Canonical dataset does not match expected schema."
    )

    # Ensure no negative emissions values
    assert (combined_df["value"] >= 0).all(), (
        "Negative emissions values detected."
    )

    return combined_df