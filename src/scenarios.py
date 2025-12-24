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

from src.config import (
    BASELINE_SCENARIO,
    NET_ZERO_SCENARIO,
    ANNUALIZE_START_YEAR,
    ANNUALIZE_END_YEAR,
    ANNUALIZATION_METHOD,
    WORLD_REGION_NAME,
    HISTORICAL_END_YEAR,
)


def compute_trajectories(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute annual emissions trajectories by scenario.
    """
    required_cols = {"year", "scenario", "sector", "value", "region"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Canonical dataset missing required columns: {sorted(missing)}")

    # Restrict to World region only (defensive; pipeline intends World scope)
    df = df[df["region"] == WORLD_REGION_NAME].copy()

    # Keep only scenarios we analyze (+ historical)
    trajectories = df[
        df["scenario"].isin(["historical", BASELINE_SCENARIO, NET_ZERO_SCENARIO])
    ].copy()

    # If upstream provided multiple rows per (year, scenario, sector), aggregate deterministically.
    trajectories = (
        trajectories.groupby(["year", "scenario", "sector"], as_index=False)["value"]
        .sum()
        .sort_values(["sector", "scenario", "year"])
    )

    return trajectories


def annualize_trajectories(
    trajectories: pd.DataFrame,
    start_year: int = ANNUALIZE_START_YEAR,
    end_year: int = ANNUALIZE_END_YEAR,
    method: str = ANNUALIZATION_METHOD,
) -> pd.DataFrame:
    """
    Annualize scenario trajectories (and optionally sector series) to yearly frequency.

    Why:
    - IEA provides milestone years (e.g., 2035/2040/2050) for scenarios.
    - Many metrics (cumulative emissions, carbon cost) require annual values.

    Approach:
    - For each (scenario, sector), reindex to [start_year..end_year]
    - Interpolate linearly across missing years
    - This *implicitly* bridges the last historical point (from OWID) to the first IEA milestone
      if both exist in the trajectory table for that sector.
    """
    df = trajectories.copy()

    required_cols = {"year", "scenario", "sector", "value"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Trajectories missing required columns: {sorted(missing)}")

    year_index = pd.Index(range(start_year, end_year + 1), name="year")

    out = []
    for (scenario, sector), g in df.groupby(["scenario", "sector"]):
        g = g.sort_values("year").set_index("year")

        # Reindex to full yearly grid then interpolate
        g2 = g.reindex(year_index)
        g2["scenario"] = scenario
        g2["sector"] = sector
        # Only interpolate between known points; do NOT extrapolate backwards.
        # This avoids fabricating pre-scenario sector series where no anchor exists.
        g2["value"] = g2["value"].interpolate(method=method, limit_area="inside")

        # If we have a last observed value, forward-fill to end_year (common for scenario end).
        g2["value"] = g2["value"].ffill()

        # Keep only annualized window (drop years still missing)
        g2 = g2.reset_index()
        g2 = g2.dropna(subset=["value"])
        out.append(g2[["year", "scenario", "sector", "value"]])

    annual = pd.concat(out, ignore_index=True)
    annual = annual.sort_values(["sector", "scenario", "year"]).reset_index(drop=True)
    return annual


def compute_gap_vs_baseline(trajectories: pd.DataFrame) -> pd.DataFrame:
    """
    Compute absolute emissions gap between baseline and net zero scenarios.
    """
    required_cols = {"year", "scenario", "sector", "value"}
    missing = required_cols - set(trajectories.columns)
    if missing:
        raise ValueError(f"Trajectories missing required columns: {sorted(missing)}")

    pivot_df = trajectories.pivot_table(
        index=["year", "sector"],
        columns="scenario",
        values="value",
        aggfunc="sum",
    )

    required = {BASELINE_SCENARIO, NET_ZERO_SCENARIO}
    if not required.issubset(pivot_df.columns):
        raise ValueError(
            f"Both {BASELINE_SCENARIO} and {NET_ZERO_SCENARIO} must be present in the dataset."
        )

    gap = (
        pivot_df[BASELINE_SCENARIO] - pivot_df[NET_ZERO_SCENARIO]
    ).reset_index(name="gap_abs")

    # Optional percent gap (relative to baseline); safe divide
    gap["gap_pct_of_baseline"] = (gap["gap_abs"] / pivot_df[BASELINE_SCENARIO].to_numpy()) * 100

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
        .groupby(["scenario", "sector"])["value"]
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
    df = trajectories.copy()
    df = df.sort_values(["sector", "scenario", "year"]).reset_index(drop=True)
    base = df.groupby(["scenario", "sector"])["value"].transform("first")
    df["emissions_index"] = (df["value"] / base) * 100
    return df


def run_scenario_analysis(df: pd.DataFrame) -> dict:
    """
    Run the full scenario analysis.
    """
    trajectories_raw = compute_trajectories(df)

    # -----------------------------------------------------------------
    # Build scenario series anchored to history (needed for 2020–2034)
    # -----------------------------------------------------------------
    # We assume scenario pathways follow observed history up to HISTORICAL_END_YEAR,
    # then transition to the IEA milestone pathway (e.g., 2035/2040/2050).
    history = trajectories_raw[trajectories_raw["scenario"] == "historical"].copy()
    scenario_points = trajectories_raw[
        trajectories_raw["scenario"].isin([BASELINE_SCENARIO, NET_ZERO_SCENARIO])
    ].copy()

    # Anchor only sectors present in history (in this project: Total energy supply)
    anchor_sectors = sorted(history["sector"].unique().tolist())
    anchored_rows = []
    for scen in [BASELINE_SCENARIO, NET_ZERO_SCENARIO]:
        h = history[history["sector"].isin(anchor_sectors) & (history["year"] <= HISTORICAL_END_YEAR)].copy()
        h["scenario"] = scen
        anchored_rows.append(h)

    scenario_with_history = pd.concat([scenario_points, *anchored_rows], ignore_index=True)

    # Annualize to enable correct cumulative + risk calculations.
    trajectories = annualize_trajectories(scenario_with_history)

    gaps = compute_gap_vs_baseline(trajectories)
    cumulative = compute_cumulative_emissions(trajectories, start_year=ANNUALIZE_START_YEAR)
    indexed = compute_indexed_trajectories(trajectories)

    return {
        "trajectories": trajectories,
        "trajectories_raw": trajectories_raw,
        "scenario_points": scenario_points,
        "gaps": gaps,
        "cumulative": cumulative,
        "indexed": indexed,
    }