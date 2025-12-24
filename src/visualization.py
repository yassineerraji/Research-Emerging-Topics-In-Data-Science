"""
visualization.py

Visualization utilities for the climate scenario analysis pipeline.

This module is responsible for generating static, publication-grade figures
from pre-computed analysis results. It does not perform any data loading
or analytical computations.
"""

import matplotlib.pyplot as plt

from src.config import FIGURES_DIR, EMISSIONS_UNIT


def plot_emissions_trajectories(df):
    """
    Plot global CO2 emissions trajectories by scenario.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing emissions trajectories with columns:
        - year
        - scenario
        - value
    """
    plt.figure(figsize=(10, 6))

    # Plot each scenario separately for clarity
    for scenario in df["scenario"].unique():
        subset = df[df["scenario"] == scenario]
        plt.plot(
            subset["year"],
            subset["value"],
            label=scenario,
        )

    plt.xlabel("Year")
    plt.ylabel(f"CO2 emissions ({EMISSIONS_UNIT})")
    plt.title("Global CO2 Emissions Trajectories by Scenario")
    plt.legend()
    plt.grid(True, alpha=0.3)

    output_path = FIGURES_DIR / "emissions_trajectories.png"
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def plot_emissions_gap(df):
    """
    Plot the absolute emissions gap between baseline and net-zero scenarios.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing gap metrics with columns:
        - year
        - absolute_gap
    """
    plt.figure(figsize=(10, 6))

    plt.plot(
        df["year"],
        df["absolute_gap"],
        label="Baseline vs Net Zero gap",
    )

    plt.xlabel("Year")
    plt.ylabel(f"Emissions gap ({EMISSIONS_UNIT})")
    plt.title("Absolute CO2 Emissions Gap vs Baseline Scenario")
    plt.legend()
    plt.grid(True, alpha=0.3)

    output_path = FIGURES_DIR / "emissions_gap_vs_baseline.png"
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    