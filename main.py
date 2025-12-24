"""
main.py

Main execution script for the climate scenario analysis pipeline.

Running this script will:
1. Load raw OWID and IEA datasets
2. Process and harmonize data into a canonical format
3. Run scenario-based emissions analysis
4. Generate and save analysis figures
5. Run an ML extension: unsupervised regime clustering (interpretation layer)

This script is the single entry point for reproducing all results.
"""

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
)
from src.utils import log_step
from src.ml_analysis import build_ml_features, cluster_decarbonization_regimes


TABLES_DIR = Path("outputs/tables")
TABLES_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    """Run the full climate scenario analysis pipeline."""
    # -----------------------------
    # Load raw datasets
    # -----------------------------
    log_step("Loading raw datasets")
    owid_raw = load_owid_raw()
    iea_raw = load_iea_annex()

    # -----------------------------
    # Process datasets
    # -----------------------------
    log_step("Processing and harmonizing datasets")
    owid_processed = process_owid_data(owid_raw)
    iea_processed = process_iea_data(iea_raw)

    # -----------------------------
    # Build canonical dataset
    # -----------------------------
    log_step("Building canonical dataset")
    canonical_df = build_canonical_dataset(
        owid_processed,
        iea_processed,
    )

    # -----------------------------
    # Scenario analysis
    # -----------------------------
    log_step("Running scenario-based emissions analysis")
    results = run_scenario_analysis(canonical_df)

    # Save cumulative table (already part of enrichment)
    log_step("Saving cumulative emissions table")
    results["cumulative"].to_csv(
        TABLES_DIR / "cumulative_emissions_by_scenario.csv",
        index=False,
    )

    # -----------------------------
    # Core figures
    # -----------------------------
    log_step("Generating and saving core figures")
    plot_emissions_trajectories(results["trajectories"])
    plot_emissions_gap(results["gaps"])
    plot_cumulative_emissions(results["cumulative"])

    # If you already added indexed outputs earlier, this will work directly.
    # If not, ensure your scenario analysis dict contains "indexed".
    if "indexed" in results:
        plot_indexed_trajectories(results["indexed"])

    # -----------------------------
    # ML extension (interpretation layer)
    # -----------------------------
    log_step("Running ML extension: regime clustering (unsupervised)")

    ml_features = build_ml_features(results["trajectories"], start_year=2020)
    ml_clustered = cluster_decarbonization_regimes(ml_features, k=3, random_state=42)

    # Save ML tables for reproducibility and report appendix
    log_step("Saving ML feature and clustering tables")
    ml_features.to_csv(TABLES_DIR / "ml_features.csv", index=False)
    ml_clustered.to_csv(TABLES_DIR / "ml_cluster_assignments.csv", index=False)

    # ML visualization
    log_step("Generating ML regime clustering figure")
    plot_ml_regimes(ml_clustered)

    log_step("Pipeline execution completed successfully")


if __name__ == "__main__":
    main()