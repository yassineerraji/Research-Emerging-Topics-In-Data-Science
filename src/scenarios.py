"""
scenarios.py

Scenario-based analysis logic for the climate scenario analysis pipeline.

This module computes:
- annual emissions trajectories by scenario
- absolute emissions gaps vs baseline
- cumulative emissions metrics
- indexed (normalized) emissions trajectories
"""

import pandas as pd

from src.config import BASELINE_SCENARIO, NET_ZERO_SCENARIO


def compute_trajectories(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute annual emissions trajectories by scenario.
    """
    trajectories = (
        df[df["scenario"].isin(["historical", BASELINE_SCENARIO, NET_ZERO_SCENARIO])]
        .groupby(["year", "scenario"], as_index=False)["value"]
        .sum()
        .sort_values(["scenario", "year"])
    )

    return trajectories


def compute_gap_vs_baseline(trajectories: pd.DataFrame) -> pd.DataFrame:
    """
    Compute absolute emissions gap between baseline and net zero scenarios.
    """
    pivot_df = trajectories.pivot(
        index="year",
        columns="scenario",
        values="value",
    )

    required = {BASELINE_SCENARIO, NET_ZERO_SCENARIO}
    if not required.issubset(pivot_df.columns):
        raise ValueError(
            f"Both {BASELINE_SCENARIO} and {NET_ZERO_SCENARIO} must be present in the dataset."
        )

    gap = (
        pivot_df[BASELINE_SCENARIO] - pivot_df[NET_ZERO_SCENARIO]
    ).reset_index(name="gap")

    return gap


def compute_cumulative_emissions(
    trajectories: pd.DataFrame,
    start_year: int = 2020,
) -> pd.DataFrame:
    """
    Compute cumulative emissions by scenario from a given start year.
    """
    df = trajectories[trajectories["year"] >= start_year].copy()

    df["cumulative_emissions"] = (
        df.sort_values("year")
        .groupby("scenario")["value"]
        .cumsum()
    )

    return df


def compute_indexed_trajectories(
    trajectories: pd.DataFrame,
) -> pd.DataFrame:
    """
    Compute indexed (normalized) emissions trajectories.

    Each scenario is normalized to 100 in its first available year.
    This highlights relative rates of change rather than absolute levels.
    """
    indexed = trajectories.copy()

    def normalize(group: pd.DataFrame) -> pd.DataFrame:
        base_value = group.iloc[0]["value"]
        group["emissions_index"] = (group["value"] / base_value) * 100
        return group

    indexed = (
        indexed.sort_values("year")
        .groupby("scenario", group_keys=False)
        .apply(normalize)
    )

    return indexed


def run_scenario_analysis(df: pd.DataFrame) -> dict:
    """
    Run the full scenario analysis.
    """
    trajectories = compute_trajectories(df)
    gaps = compute_gap_vs_baseline(trajectories)
    cumulative = compute_cumulative_emissions(trajectories)
    indexed = compute_indexed_trajectories(trajectories)

    return {
        "trajectories": trajectories,
        "gaps": gaps,
        "cumulative": cumulative,
        "indexed": indexed,
    }