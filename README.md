# Climate Scenario Pipeline

## Project Overview
This project provides a comprehensive pipeline for analyzing climate scenario data, including data processing, scenario extraction, trend projection, and visualization capabilities. It is designed to work with climate model outputs and projections under different Representative Concentration Pathways (RCPs).

## Dependencies

### Required Python Packages
```bash
pip install -r requirements.txt
```

Core dependencies:
- `pandas` - Data manipulation and analysis
- `numpy` - Numerical computing
- `scikit-learn` - Machine learning and statistical analysis
- `matplotlib` - Data visualization
- `seaborn` - Statistical data visualization
- `requests` - Data downloading capabilities

## Project Structure
```
climate-scenario-pipeline/
├── README.md
├── main.py                  # Main execution script
├── requirements.txt         # Python dependencies
├── data/
│   ├── raw/                # Raw downloaded data (unmodified)
│   ├── interim/            # Cleaned intermediate data
│   └── processed/          # Final modeling-ready data
├── outputs/
│   ├── figures/            # Generated plots and visualizations
│   └── tables/             # Summary tables and statistics
└── src/
    ├── __init__.py         # Package initialization
    ├── config.py           # Configuration and paths
    ├── io.py               # Data loading/saving utilities
    ├── processing.py       # Data cleaning and harmonization
    ├── scenarios.py        # Scenario extraction and analysis
    ├── visualization.py    # Plotting functions
    └── utils.py            # Helper utilities
```

## Input Data

### Expected Data Format
Place your climate data CSV files in the `data/raw/` directory. The expected format includes:

**Required columns:**
- **Date/Time column**: Date, time, or year information
- **Scenario column**: Climate scenario identifier (e.g., RCP2.6, RCP4.5, RCP6.0, RCP8.5)
- **Value columns**: Climate variables (e.g., temperature, precipitation, sea level)

**Optional columns:**
- **Region/Location**: Geographic identifiers for spatial analysis

### Example Data Structure
```csv
date,scenario,temperature,precipitation,region
2020-01-01,RCP4.5,15.2,45.3,North America
2020-01-01,RCP8.5,15.8,47.1,North America
...
```

## Execution Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Prepare Data
Place your climate scenario data files (CSV format) in the `data/raw/` directory.

### 3. Run the Pipeline
Execute the main script to run the complete analysis pipeline:
```bash
python main.py
```

The pipeline will:
1. **Load data** from `data/raw/`
2. **Assess data quality** and report statistics
3. **Clean and process** data (handle missing values, outliers)
4. **Extract and analyze scenarios** across different RCPs
5. **Generate visualizations** (time series, comparisons, distributions)
6. **Export results** to `outputs/` directory

## Output

Results are organized in the `outputs/` directory:

### Figures (`outputs/figures/`)
- `scenario_comparison.png` - Time series comparison across scenarios
- `distribution_comparison.png` - Statistical distributions by scenario
- `dashboard.png` - Multi-panel overview dashboard
- Additional custom visualizations

### Tables (`outputs/tables/`)
- `scenario_summary.csv` - Statistical summary by scenario
- Custom analysis tables

### Processed Data (`data/`)
- `data/interim/cleaned_data.csv` - Cleaned intermediate data
- `data/processed/` - Final modeling-ready datasets

## Module Usage

### Using Individual Components

You can import and use individual modules for custom analysis:

```python
from src import config, io, processing, scenarios, visualization

# Load data
data = io.load_raw_data('your_data.csv')

# Clean data
clean_data = processing.clean_missing_values(data)

# Extract specific scenario
rcp45_data = scenarios.extract_scenario_data(data, 'scenario', 'RCP4.5')

# Create visualizations
visualization.plot_scenario_comparison(
    data, 
    datetime_col='date',
    value_col='temperature',
    scenario_col='scenario'
)
```

### Configuration

Modify settings in `src/config.py`:
- Data source URLs
- Processing parameters (missing value strategy, outlier thresholds)
- Scenario definitions (RCP scenarios, time periods)
- Visualization settings (DPI, color schemes)

## Advanced Features

### Scenario Analysis
- Multi-scenario comparison
- Anomaly computation relative to baseline periods
- Trend projection and extrapolation
- Scenario divergence analysis
- Ensemble projections

### Data Processing
- Temporal and spatial harmonization
- Unit conversion utilities
- Rolling statistics and feature engineering
- Outlier detection and removal

### Visualization
- Time series plots with uncertainty bands
- Heatmaps for spatiotemporal patterns
- Distribution comparisons
- Comprehensive dashboards

## Troubleshooting

**No data files found:**
- Ensure CSV files are placed in `data/raw/`
- Check file permissions

**Missing columns error:**
- Verify your data includes date, scenario, and value columns
- Check column naming conventions

**Memory issues with large datasets:**
- Process data in chunks
- Use data type optimization in `processing.py`

## Contributing
This is an academic project for Research & Emerging Topics in Data Science.

## License
Academic project - All rights reserved.

## Contact
For questions or issues, please contact the project maintainer.
