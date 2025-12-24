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


def plot_emissions_trajectories(df: pd.DataFrame, sector: str = "Total energy supply") -> None:
    plt.figure(figsize=(10, 6))
    sub = df[df["sector"] == sector] if "sector" in df.columns else df
    for scenario, sub_df in sub.groupby("scenario"):
        plt.plot(sub_df["year"], sub_df["value"], label=scenario)
    plt.title(f"CO2 Emissions Trajectories by Scenario ({sector})")
    plt.xlabel("Year")
    plt.ylabel("CO2 emissions (MtCO2)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "emissions_trajectories_by_scenario.png", dpi=300)
    plt.close()


def plot_emissions_gap(df: pd.DataFrame, sector: str = "Total energy supply") -> None:
    plt.figure(figsize=(10, 6))
    sub = df[df["sector"] == sector] if "sector" in df.columns else df
    plt.plot(sub["year"], sub["gap_abs"], label="STEPS - NZE (absolute gap)")
    plt.title(f"Absolute CO2 Emissions Gap vs Baseline ({sector})")
    plt.xlabel("Year")
    plt.ylabel("Emissions gap (MtCO2)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "emissions_gap_vs_baseline.png", dpi=300)
    plt.close()


def plot_cumulative_emissions(df: pd.DataFrame, sector: str = "Total energy supply") -> None:
    plt.figure(figsize=(10, 6))
    sub = df[df["sector"] == sector] if "sector" in df.columns else df
    for scenario, sub_df in sub.groupby("scenario"):
        plt.plot(sub_df["year"], sub_df["cumulative_emissions"], label=scenario)
    plt.title(f"Cumulative CO2 Emissions by Scenario (from 2020) ({sector})")
    plt.xlabel("Year")
    plt.ylabel("Cumulative CO2 emissions (MtCO2)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "cumulative_emissions_by_scenario.png", dpi=300)
    plt.close()


def plot_indexed_trajectories(df: pd.DataFrame, sector: str = "Total energy supply") -> None:
    plt.figure(figsize=(10, 6))
    sub = df[df["sector"] == sector] if "sector" in df.columns else df
    for scenario, sub_df in sub.groupby("scenario"):
        plt.plot(sub_df["year"], sub_df["emissions_index"], label=scenario)
    plt.axhline(100, linestyle="--", linewidth=1)
    plt.title(f"Indexed CO2 Emissions Trajectories (Index = 100 at Start) ({sector})")
    plt.xlabel("Year")
    plt.ylabel("Emissions index")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "indexed_emissions_trajectories.png", dpi=300)
    plt.close()


def plot_ml_regimes(df: pd.DataFrame) -> None:
    plt.figure(figsize=(10, 6))
    for scenario, sub_df in df.groupby("scenario"):
        plt.scatter(
            sub_df["year"],
            sub_df["emissions_index"],
            c=sub_df["cluster"],
            label=scenario,
            alpha=0.9,
        )
    plt.title("ML Regime Clustering of Decarbonization Dynamics (Global)")
    plt.xlabel("Year")
    plt.ylabel("Emissions index (Index = 100 at scenario start)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "ml_regime_clustering.png", dpi=300)
    plt.close()


def plot_country_clusters_pca(pca_df: pd.DataFrame) -> None:
    """
    Plot country-level clustering in PCA space.

    Expected columns:
    - pca1
    - pca2
    - cluster
    """
    plt.figure(figsize=(12, 7))

    plt.scatter(
        pca_df["pca1"],
        pca_df["pca2"],
        c=pca_df["cluster"],
        alpha=0.85,
    )

    plt.title("Country-Level Decarbonization Regimes (PCA projection)")
    plt.xlabel("PCA component 1")
    plt.ylabel("PCA component 2")
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(FIGURES_DIR / "country_ml_clusters_pca.png", dpi=300)
    plt.close()


def plot_carbon_cost(cost_df: pd.DataFrame, sector: str = "Total energy supply") -> None:
    """
    Plot annual carbon cost (USD bn) by scenario for a given sector.
    """
    plt.figure(figsize=(10, 6))
    sub = cost_df[cost_df["sector"] == sector] if "sector" in cost_df.columns else cost_df
    for scenario, g in sub.groupby("scenario"):
        plt.plot(g["year"], g["carbon_cost_usd_bn"], label=scenario)
    plt.title(f"Carbon Cost Stress Test (USD bn) ({sector})")
    plt.xlabel("Year")
    plt.ylabel("Carbon cost (USD bn)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "carbon_cost_by_scenario.png", dpi=300)
    plt.close()


def plot_sector_trajectories_grid(
    df: pd.DataFrame,
    start_year: int = 2035,
    exclude_total: bool = False,
) -> None:
    """
    Small-multiples plot of emissions trajectories by sector (IEA FLOW).
    Intended for sector-level deliverable coverage.
    """
    required = {"year", "scenario", "sector", "value"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"plot_sector_trajectories_grid missing columns: {sorted(missing)}")

    sub = df[df["year"] >= start_year].copy()
    sectors = sorted(sub["sector"].unique().tolist())
    if exclude_total:
        sectors = [s for s in sectors if s != "Total energy supply"]

    n = len(sectors)
    if n == 0:
        return

    ncols = 2
    nrows = (n + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(12, 4 * nrows), squeeze=False)

    for i, sector in enumerate(sectors):
        ax = axes[i // ncols][i % ncols]
        g = sub[sub["sector"] == sector]
        for scen, gg in g.groupby("scenario"):
            ax.plot(gg["year"], gg["value"], label=scen)
        ax.set_title(sector)
        ax.set_xlabel("Year")
        ax.set_ylabel("MtCO2")
        ax.grid(True)
        ax.legend()

    # Hide any unused axes
    for j in range(n, nrows * ncols):
        axes[j // ncols][j % ncols].axis("off")

    fig.suptitle("Sector-level CO2 emissions trajectories (IEA flows)", y=0.995)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "sector_emissions_trajectories_grid.png", dpi=300)
    plt.close(fig)