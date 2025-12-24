"""
main.py

Main execution script for the climate scenario analysis pipeline.

Running this script will:
1. Load raw OWID and IEA datasets
2. Process and harmonize data into a canonical format
3. Run scenario-based emissions analysis
4. Generate and save analysis figures

This script is the single entry point for reproducing all results.
"""

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
)
from src.utils import log_step


def main() -> None:
    """
    Run the full climate scenario analysis pipeline.

    This function orchestrates the end-to-end workflow without performing
    any data processing, analysis logic, or visualization itself.
    """
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
    # Run scenario analysis
    # -----------------------------
    log_step("Running scenario-based emissions analysis")
    analysis_results = run_scenario_analysis(canonical_df)

    # -----------------------------
    # Generate figures
    # -----------------------------
    log_step("Generating and saving figures")
    plot_emissions_trajectories(analysis_results["trajectories"])
    plot_emissions_gap(analysis_results["gaps"])

    log_step("Pipeline execution completed successfully")


if __name__ == "__main__":
    main()