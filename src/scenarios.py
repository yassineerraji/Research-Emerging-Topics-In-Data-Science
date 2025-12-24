"""
scenarios.py

Scenario analysis logic for the climate emissions pipeline.

This module extracts scenario-specific emissions trajectories from the
canonical dataset and computes comparative metrics between baseline and
net-zero pathways.

No data loading or visualization occurs here.
"""

import pandas as pd

from src.config import (
    BASELINE_SCENARIO,
    NET_ZERO_SCENARIO,
    CO2_VARIABLE_NAME,
)


def extract_scenario_trajectories(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract emissions trajectories for each scenario.

    Parameters
    ----------
    df : pd.DataFrame
        Canonical dataset containing historical and scenario data.

    Returns
    -------
    pd.DataFrame
        DataFrame with emissions trajectories by year and scenario.
    """
    # Keep only CO2 emissions variable
    df = df[df["variable"] == CO2_VARIABLE_NAME].copy()

    # Aggregate in case multiple rows exist per year/scenario
    trajectories = (
        df.groupby(["year", "scenario"], as_index=False)["value"]
        .sum()
    )

    return trajectories


def compute_gap_vs_baseline(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute absolute and relative emissions gaps between the baseline
    scenario and the net-zero scenario.

    Parameters
    ----------
    df : pd.DataFrame
        Output of extract_scenario_trajectories().

    Returns
    -------
    pd.DataFrame
        DataFrame containing absolute and percentage gaps by year.
    """
    # Pivot to wide format for easier comparison
    pivot_df = df.pivot(
        index="year",
        columns="scenario",
        values="value",
    ).reset_index()

    # Ensure required scenarios are present
    required = {BASELINE_SCENARIO, NET_ZERO_SCENARIO}
    if not required.issubset(pivot_df.columns):
        raise ValueError(
            f"Both {BASELINE_SCENARIO} and {NET_ZERO_SCENARIO} "
            "must be present in the dataset."
        )

    # Compute absolute gap (baseline - net zero)
    pivot_df["absolute_gap"] = (
        pivot_df[BASELINE_SCENARIO] - pivot_df[NET_ZERO_SCENARIO]
    )

    # Compute relative gap (% reduction vs baseline)
    pivot_df["relative_gap_pct"] = (
        pivot_df["absolute_gap"] / pivot_df[BASELINE_SCENARIO]
    ) * 100

    return pivot_df


def run_scenario_analysis(df: pd.DataFrame) -> dict:
    """
    Run the full scenario analysis workflow.

    Parameters
    ----------
    df : pd.DataFrame
        Canonical dataset.

    Returns
    -------
    dict
        Dictionary containing analysis outputs:
        - trajectories
        - gaps
    """
    trajectories = extract_scenario_trajectories(df)
    gaps = compute_gap_vs_baseline(trajectories)

    return {
        "trajectories": trajectories,
        "gaps": gaps,
    }