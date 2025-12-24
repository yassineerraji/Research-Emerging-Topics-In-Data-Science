"""
main.py

Main execution script for the climate scenario analysis pipeline.

Running this script will:
1. Load raw OWID and IEA datasets
2. Process and harmonize data into a canonical format
3. Run scenario-based emissions analysis
4. Generate and save analysis figures and tables
5. Run ML extensions:
   - Global illustrative regime clustering (small sample)
   - Country-level regime clustering (substantive, recommended)

This script is the single entry point for reproducing all results.
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from src.io import load_owid_raw, load_iea_annex
from src.processing import (
    process_owid_data,
    process_iea_data,
    build_canonical_dataset,
)
from src.scenarios import run_scenario_analysis
from src.visualization import (
    plot_emissions_trajectories,
    plot_emissions_gap,
    plot_cumulative_emissions,
    plot_indexed_trajectories,
    plot_ml_regimes,
    plot_country_clusters_pca,
    plot_carbon_cost,
    plot_sector_trajectories_grid,
)
from src.utils import log_step
from src.config import TABLES_DIR, PROCESSED_DATA_DIR
from src.ml_analysis import (
    build_ml_features,
    cluster_decarbonization_regimes,
    CountryMLConfig,
    build_country_ml_features,
    cluster_country_regimes,
)
from src.risk import (
    build_default_carbon_price_paths,
    compute_carbon_cost,
    compute_cumulative_carbon_cost,
)

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Climate scenario + transition risk pipeline")
    p.add_argument(
        "--main-sector",
        default="Total energy supply",
        help="Sector (IEA FLOW) to use for headline plots (default: Total energy supply).",
    )
    p.add_argument(
        "--run-ml",
        action="store_true",
        default=False,
        help="Run ML extensions (global + country-level). Off by default for faster runs.",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()

    log_step("Loading raw datasets")
    owid_raw = load_owid_raw()
    iea_raw = load_iea_annex()

    log_step("Processing and harmonizing datasets")
    owid_processed = process_owid_data(owid_raw)
    iea_processed = process_iea_data(iea_raw)

    log_step("Building canonical dataset")
    canonical_df = build_canonical_dataset(owid_processed, iea_processed)

    log_step("Saving canonical processed dataset")
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    canonical_df.to_csv(PROCESSED_DATA_DIR / "canonical_emissions.csv", index=False)

    log_step("Running scenario-based emissions analysis")
    results = run_scenario_analysis(canonical_df)

    log_step("Saving scenario analysis tables")
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    results["trajectories_raw"].to_csv(TABLES_DIR / "trajectories_raw.csv", index=False)
    results["scenario_points"].to_csv(TABLES_DIR / "scenario_points_iea.csv", index=False)
    results["trajectories"].to_csv(TABLES_DIR / "trajectories_annual.csv", index=False)
    results["gaps"].to_csv(TABLES_DIR / "emissions_gap_by_sector.csv", index=False)
    results["cumulative"].to_csv(TABLES_DIR / "cumulative_emissions_by_scenario.csv", index=False)
    results["indexed"].to_csv(TABLES_DIR / "indexed_emissions_trajectories.csv", index=False)

    log_step("Generating and saving core figures")
    # Use raw trajectories to show historical context, but filter headline sector.
    plot_emissions_trajectories(results["trajectories_raw"], sector=args.main_sector)
    plot_emissions_gap(results["gaps"], sector=args.main_sector)
    plot_cumulative_emissions(results["cumulative"], sector=args.main_sector)

    # If present, indexed plot
    if "indexed" in results:
        plot_indexed_trajectories(results["indexed"], sector=args.main_sector)

    # Sector-level figure (IEA flows): small multiples
    plot_sector_trajectories_grid(results["trajectories"], start_year=2035, exclude_total=False)

    # -----------------------------------------------------------------
    # Transition risk layer: carbon price stress test
    # -----------------------------------------------------------------
    log_step("Running transition risk layer: carbon price stress test")
    carbon_prices = build_default_carbon_price_paths()
    carbon_cost = compute_carbon_cost(results["trajectories"], carbon_prices)
    carbon_cost_cum = compute_cumulative_carbon_cost(carbon_cost, start_year=2020)

    log_step("Saving transition risk tables")
    carbon_prices.to_csv(TABLES_DIR / "carbon_price_paths.csv", index=False)
    carbon_cost.to_csv(TABLES_DIR / "carbon_cost_annual.csv", index=False)
    carbon_cost_cum.to_csv(TABLES_DIR / "carbon_cost_cumulative.csv", index=False)

    log_step("Generating transition risk figure")
    plot_carbon_cost(carbon_cost, sector=args.main_sector)

    # -----------------------------------------------------------------
    # Run metadata (reproducibility)
    # -----------------------------------------------------------------
    log_step("Saving run metadata")
    metadata = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "main_sector": args.main_sector,
        "run_ml": bool(args.run_ml),
        "raw_files": {
            "owid": str(Path("data/raw/owid-co2-data.csv").resolve()),
            "iea": str(Path("data/raw/WEO2025_AnnexA_Free_Dataset_World.csv").resolve()),
        },
        "outputs": {
            "tables_dir": str(TABLES_DIR.resolve()),
            "processed_dir": str(PROCESSED_DATA_DIR.resolve()),
        },
    }
    (TABLES_DIR / "run_metadata.json").write_text(json.dumps(metadata, indent=2))

    # -----------------------------------------------------------------
    # ML extension (A): global illustrative clustering
    # -----------------------------------------------------------------
    if args.run_ml:
        log_step("Running ML extension (global): regime clustering (unsupervised)")
        # Global ML is illustrative only; use total sector only.
        ml_traj = results["trajectories"][results["trajectories"]["sector"] == args.main_sector].copy()
        ml_features = build_ml_features(ml_traj.rename(columns={"sector": "sector_tmp"}), start_year=2020)
        ml_clustered = cluster_decarbonization_regimes(ml_features, k=3, random_state=42)

        log_step("Saving ML (global) feature and clustering tables")
        ml_features.to_csv(TABLES_DIR / "ml_features.csv", index=False)
        ml_clustered.to_csv(TABLES_DIR / "ml_cluster_assignments.csv", index=False)

        log_step("Generating ML (global) regime clustering figure")
        plot_ml_regimes(ml_clustered)

    # -----------------------------------------------------------------
    # ML extension (B): country-level clustering (substantive)
    # -----------------------------------------------------------------
    if args.run_ml:
        log_step("Running ML extension (country-level): regime clustering from OWID")
        cfg = CountryMLConfig(start_year=2010, end_year=2023, k=4, random_state=42, min_years_required=10)

        country_features = build_country_ml_features(owid_raw, cfg=cfg)
        country_clustered, country_pca = cluster_country_regimes(country_features, cfg=cfg)

        log_step("Saving ML (country-level) feature and clustering tables")
        country_features.to_csv(TABLES_DIR / "country_ml_features.csv", index=False)
        country_clustered.to_csv(TABLES_DIR / "country_ml_cluster_assignments.csv", index=False)
        country_pca.to_csv(TABLES_DIR / "country_ml_pca_coords.csv", index=False)

        log_step("Generating ML (country-level) PCA clustering figure")
        plot_country_clusters_pca(country_pca)

    log_step("Pipeline execution completed successfully")


if __name__ == "__main__":
    main()