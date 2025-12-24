"""
main.py

Main execution script for the climate scenario analysis pipeline.
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
    plot_cumulative_emissions,
    plot_indexed_trajectories
)
from src.utils import log_step
from pathlib import Path


TABLES_DIR = Path("outputs/tables")
TABLES_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    log_step("Loading raw datasets")
    owid_raw = load_owid_raw()
    iea_raw = load_iea_annex()

    log_step("Processing and harmonizing datasets")
    owid_processed = process_owid_data(owid_raw)
    iea_processed = process_iea_data(iea_raw)

    log_step("Building canonical dataset")
    canonical_df = build_canonical_dataset(
        owid_processed,
        iea_processed,
    )

    log_step("Running scenario-based emissions analysis")
    results = run_scenario_analysis(canonical_df)

    log_step("Saving cumulative emissions table")
    results["cumulative"].to_csv(
        TABLES_DIR / "cumulative_emissions_by_scenario.csv",
        index=False,
    )

    log_step("Generating figures")
    plot_emissions_trajectories(results["trajectories"])
    plot_emissions_gap(results["gaps"])
    plot_cumulative_emissions(results["cumulative"])
    plot_indexed_trajectories(results["indexed"])

    log_step("Pipeline execution completed successfully")


if __name__ == "__main__":
    main()
