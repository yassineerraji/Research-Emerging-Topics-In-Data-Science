"""
config.py

Central configuration file for the climate scenario analysis pipeline.

This module defines:
- file paths
- canonical schema conventions
- scenario names
- units and time boundaries

The goal is to avoid hardcoding values throughout the codebase and
ensure consistency, reproducibility, and transparency.
"""

from pathlib import Path

# =========================
# Project root and paths
# =========================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
INTERIM_DATA_DIR = DATA_DIR / "interim"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

OUTPUTS_DIR = PROJECT_ROOT / "outputs"
FIGURES_DIR = OUTPUTS_DIR / "figures"
TABLES_DIR = OUTPUTS_DIR / "tables"

# Ensure output directories exist (safe to call multiple times)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)

# =========================
# Raw data file names
# =========================

OWID_CO2_FILE = RAW_DATA_DIR / "owid-co2-data.csv"
IEA_ANNEX_FILE = RAW_DATA_DIR / "WEO2025_AnnexA_Free_Dataset_World.csv"

# =========================
# Scope restrictions
# =========================

# We explicitly restrict analysis to the global level
WORLD_REGION_NAME = "World"

# Time boundaries (inclusive)
HISTORICAL_START_YEAR = 1990
HISTORICAL_END_YEAR = 2023
SCENARIO_END_YEAR = 2050

# =========================
# Scenario configuration
# =========================

# These are the scenarios we expect to analyze.
# Names must match those used in the IEA dataset after cleaning.
BASELINE_SCENARIO = "STEPS"   # Stated Policies Scenario
NET_ZERO_SCENARIO = "NZE"     # Net Zero Emissions by 2050

ALLOWED_SCENARIOS = [
    BASELINE_SCENARIO,
    NET_ZERO_SCENARIO,
]

# =========================
# Canonical schema
# =========================

CANONICAL_COLUMNS = [
    "year",
    "region",
    "sector",
    "scenario",
    "variable",
    "value",
    "unit",
    "source",
]

# =========================
# Units
# =========================

# We standardize all emissions to megatonnes of CO2 (MtCO2)
EMISSIONS_UNIT = "MtCO2"

# =========================
# Variables of interest
# =========================

# Canonical variable name for economy-wide CO2 emissions
CO2_VARIABLE_NAME = "CO2_emissions"