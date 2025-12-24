"""
visualization.py

Visualization utilities for the climate scenario analysis pipeline.

This module generates static figures from analysis-ready data.
No data processing or scenario logic is performed here.
"""

import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path


FIGURES_DIR = Path("outputs/figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def plot_emissions_trajectories(df: pd.DataFrame) -> None:
    """Plot annual CO2 emissions trajectories by scenario."""
    plt.figure(figsize=(10, 6))

    for scenario, sub_df in df.groupby("scenario"):
        plt.plot(sub_df["year"], sub_df["value"], label=scenario)

    plt.title("Global CO2 Emissions Trajectories by Scenario")
    plt.xlabel("Year")
    plt.ylabel("CO2 emissions (MtCO2)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(FIGURES_DIR / "emissions_trajectories_by_scenario.png", dpi=300)
    plt.close()


def plot_emissions_gap(df: pd.DataFrame) -> None:
    """Plot absolute emissions gap vs baseline scenario."""
    plt.figure(figsize=(10, 6))

    plt.plot(df["year"], df["gap"], label="Baseline vs Net Zero gap")

    plt.title("Absolute CO2 Emissions Gap vs Baseline Scenario")
    plt.xlabel("Year")
    plt.ylabel("Emissions gap (MtCO2)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(FIGURES_DIR / "emissions_gap_vs_baseline.png", dpi=300)
    plt.close()


def plot_cumulative_emissions(df: pd.DataFrame) -> None:
    """Plot cumulative CO2 emissions by scenario."""
    plt.figure(figsize=(10, 6))

    for scenario, sub_df in df.groupby("scenario"):
        plt.plot(
            sub_df["year"],
            sub_df["cumulative_emissions"],
            label=scenario,
        )

    plt.title("Cumulative Global CO2 Emissions by Scenario (from 2020)")
    plt.xlabel("Year")
    plt.ylabel("Cumulative CO2 emissions (MtCO2)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(FIGURES_DIR / "cumulative_emissions_by_scenario.png", dpi=300)
    plt.close()


def plot_indexed_trajectories(df: pd.DataFrame) -> None:
    """Plot indexed (normalized) emissions trajectories."""
    plt.figure(figsize=(10, 6))

    for scenario, sub_df in df.groupby("scenario"):
        plt.plot(
            sub_df["year"],
            sub_df["emissions_index"],
            label=scenario,
        )

    plt.axhline(100, linestyle="--", linewidth=1)
    plt.title("Indexed Global CO2 Emissions Trajectories (Index = 100 at Start)")
    plt.xlabel("Year")
    plt.ylabel("Emissions index")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(FIGURES_DIR / "indexed_emissions_trajectories.png", dpi=300)
    plt.close()


def plot_ml_regimes(df: pd.DataFrame) -> None:
    """
    Plot ML-identified decarbonization regimes.

    We visualize (scenario, year) points in the indexed emissions space and color
    them by the cluster/regime label.

    Expected columns:
    - year
    - scenario
    - emissions_index
    - cluster
    """
    plt.figure(figsize=(10, 6))

    # Scatter points per scenario, colored by cluster
    # Using scatter (not lines) is intentional: clusters label points/segments.
    for scenario, sub_df in df.groupby("scenario"):
        plt.scatter(
            sub_df["year"],
            sub_df["emissions_index"],
            c=sub_df["cluster"],
            label=scenario,
            alpha=0.9,
        )

    plt.title("ML Regime Clustering of Decarbonization Dynamics")
    plt.xlabel("Year")
    plt.ylabel("Emissions index (Index = 100 at scenario start)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    plt.savefig(FIGURES_DIR / "ml_regime_clustering.png", dpi=300)
    plt.close()