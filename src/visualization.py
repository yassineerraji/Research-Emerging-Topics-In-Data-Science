"""
visualization.py

Visualization utilities for the climate scenario analysis pipeline.
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

    plt.savefig(FIGURES_DIR / "emissions_trajectories_by_scenario.png")
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

    plt.savefig(FIGURES_DIR / "emissions_gap_vs_baseline.png")
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

    plt.savefig(FIGURES_DIR / "cumulative_emissions_by_scenario.png")
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

    plt.savefig(FIGURES_DIR / "indexed_emissions_trajectories.png")
    plt.close()