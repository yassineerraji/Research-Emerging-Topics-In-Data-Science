"""
risk.py

Transition risk analytics layer for the climate scenario analysis pipeline.

This module intentionally implements a lightweight, transparent risk proxy:

- Carbon price stress test:
    annual emissions (MtCO2) x carbon price (USD/tCO2) -> annual carbon cost (USD)

This is NOT a full financial model. It is a reproducible, scenario-consistent
metric that can be extended to entity-level exposures (sectors/companies).
"""

from __future__ import annotations

import pandas as pd

from src.config import (
    BASELINE_SCENARIO,
    NET_ZERO_SCENARIO,
    CARBON_PRICE_START_YEAR,
    CARBON_PRICE_END_YEAR,
    CARBON_PRICE_START_USD_STEPS,
    CARBON_PRICE_END_USD_STEPS,
    CARBON_PRICE_START_USD_NZE,
    CARBON_PRICE_END_USD_NZE,
)


def build_default_carbon_price_paths(
    start_year: int = CARBON_PRICE_START_YEAR,
    end_year: int = CARBON_PRICE_END_YEAR,
) -> pd.DataFrame:
    """
    Build simple stylized carbon price paths for STEPS vs NZE.

    Returns
    -------
    pd.DataFrame with columns:
        - year
        - scenario
        - carbon_price_usd_per_tco2
    """
    years = list(range(start_year, end_year + 1))

    def linear_path(y0: int, y1: int, p0: float, p1: float) -> list[float]:
        if y1 == y0:
            return [p1 for _ in years]
        out = []
        for y in years:
            if y <= y0:
                out.append(p0)
            elif y >= y1:
                out.append(p1)
            else:
                t = (y - y0) / (y1 - y0)
                out.append(p0 + t * (p1 - p0))
        return out

    steps_prices = linear_path(start_year, end_year, CARBON_PRICE_START_USD_STEPS, CARBON_PRICE_END_USD_STEPS)
    nze_prices = linear_path(start_year, end_year, CARBON_PRICE_START_USD_NZE, CARBON_PRICE_END_USD_NZE)

    df = pd.concat(
        [
            pd.DataFrame({"year": years, "scenario": BASELINE_SCENARIO, "carbon_price_usd_per_tco2": steps_prices}),
            pd.DataFrame({"year": years, "scenario": NET_ZERO_SCENARIO, "carbon_price_usd_per_tco2": nze_prices}),
        ],
        ignore_index=True,
    )
    return df


def compute_carbon_cost(
    annual_trajectories: pd.DataFrame,
    carbon_prices: pd.DataFrame,
) -> pd.DataFrame:
    """
    Compute annual carbon cost from annual emissions and carbon price paths.

    Inputs
    ------
    annual_trajectories: columns ['year','scenario','sector','value'] where value is MtCO2
    carbon_prices: columns ['year','scenario','carbon_price_usd_per_tco2']

    Returns
    -------
    pd.DataFrame with columns:
        - year, scenario, sector
        - emissions_mtco2
        - carbon_price_usd_per_tco2
        - carbon_cost_usd_bn   (billions of USD)
    """
    required_traj = {"year", "scenario", "sector", "value"}
    required_price = {"year", "scenario", "carbon_price_usd_per_tco2"}
    if missing := (required_traj - set(annual_trajectories.columns)):
        raise ValueError(f"annual_trajectories missing columns: {sorted(missing)}")
    if missing := (required_price - set(carbon_prices.columns)):
        raise ValueError(f"carbon_prices missing columns: {sorted(missing)}")

    df = annual_trajectories.rename(columns={"value": "emissions_mtco2"}).copy()
    df = df.merge(carbon_prices, on=["year", "scenario"], how="inner")

    # MtCO2 -> tCO2: multiply by 1e6
    # USD -> USD bn: divide by 1e9
    df["carbon_cost_usd_bn"] = (df["emissions_mtco2"] * 1_000_000.0 * df["carbon_price_usd_per_tco2"]) / 1_000_000_000.0

    return df[
        ["year", "scenario", "sector", "emissions_mtco2", "carbon_price_usd_per_tco2", "carbon_cost_usd_bn"]
    ].copy()


def compute_cumulative_carbon_cost(cost_df: pd.DataFrame, start_year: int = 2020) -> pd.DataFrame:
    """
    Add cumulative carbon cost per (scenario, sector) from start_year.
    """
    df = cost_df[cost_df["year"] >= start_year].copy()
    df = df.sort_values(["sector", "scenario", "year"])
    df["cumulative_carbon_cost_usd_bn"] = df.groupby(["scenario", "sector"])["carbon_cost_usd_bn"].cumsum()
    return df


