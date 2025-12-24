"""
Configuration Module

Central configuration for the climate scenario pipeline.
"""

import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'
INTERIM_DATA_DIR = DATA_DIR / 'interim'
PROCESSED_DATA_DIR = DATA_DIR / 'processed'

# Output directories
OUTPUT_DIR = PROJECT_ROOT / 'outputs'
FIGURES_DIR = OUTPUT_DIR / 'figures'
TABLES_DIR = OUTPUT_DIR / 'tables'

# Ensure directories exist
for directory in [RAW_DATA_DIR, INTERIM_DATA_DIR, PROCESSED_DATA_DIR, 
                  FIGURES_DIR, TABLES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Data sources configuration
DATA_SOURCES = {
    'climate_data': {
        'url': 'https://example.com/climate_data.csv',
        'filename': 'climate_data.csv',
        'description': 'Historical climate data'
    },
    'scenario_data': {
        'url': 'https://example.com/scenario_data.csv',
        'filename': 'scenario_data.csv',
        'description': 'Climate scenario projections'
    }
}

# Processing parameters
PROCESSING_CONFIG = {
    'missing_value_strategy': 'mean',
    'outlier_threshold': 3.0,  # standard deviations
    'temporal_resolution': 'monthly',
    'spatial_resolution': 'regional'
}

# Scenario parameters
SCENARIO_CONFIG = {
    'baseline_period': (1981, 2010),
    'projection_period': (2020, 2100),
    'scenarios': ['RCP2.6', 'RCP4.5', 'RCP6.0', 'RCP8.5'],
    'variables': ['temperature', 'precipitation', 'sea_level']
}

# Visualization settings
VIZ_CONFIG = {
    'figure_format': 'png',
    'dpi': 300,
    'style': 'seaborn-v0_8-darkgrid',
    'color_palette': 'viridis'
}

# Model configuration
MODEL_CONFIG = {
    'random_state': 42,
    'test_size': 0.2,
    'cv_folds': 5
}


def get_config():
    """
    Get the complete configuration dictionary.
    
    Returns:
        dict: Configuration dictionary
    """
    return {
        'paths': {
            'project_root': PROJECT_ROOT,
            'data': DATA_DIR,
            'raw': RAW_DATA_DIR,
            'interim': INTERIM_DATA_DIR,
            'processed': PROCESSED_DATA_DIR,
            'output': OUTPUT_DIR,
            'figures': FIGURES_DIR,
            'tables': TABLES_DIR
        },
        'data_sources': DATA_SOURCES,
        'processing': PROCESSING_CONFIG,
        'scenarios': SCENARIO_CONFIG,
        'visualization': VIZ_CONFIG,
        'model': MODEL_CONFIG
    }


def print_config():
    """Print current configuration."""
    config = get_config()
    print("="*60)
    print("Climate Scenario Pipeline Configuration")
    print("="*60)
    for section, values in config.items():
        print(f"\n{section.upper()}:")
        for key, value in values.items():
            print(f"  {key}: {value}")


if __name__ == "__main__":
    print_config()
