# Climate Scenario Analysis Pipeline  
**Reproducible Analysis of Global CO₂ Emissions under IEA Transition Pathways**

---

## Project Overview

This project implements a **fully reproducible data science pipeline** to analyze **global CO₂ emissions trajectories** under alternative **energy transition scenarios** published by the International Energy Agency (IEA).

The objective is **not to forecast climate outcomes**, but to **operationalize authoritative transition scenarios** (baseline vs net-zero) in a transparent, decision-grade analytical framework.

The project is developed as part of the *Research & Emerging Topics in Data Science* course and follows best practices in research-oriented software engineering.

---

## Research Question

> How do global CO₂ emissions trajectories differ between a baseline policy pathway and a Net Zero transition pathway, and how can a reproducible data pipeline support comparative scenario analysis?

---

## Role Assumed

**Climate Data Scientist**

Focus:
- data ingestion and harmonization,
- scenario-based emissions analysis,
- reproducibility and methodological clarity.

---

## Data Sources

- **Our World in Data (OWID)**  
  Historical global CO₂ emissions (energy-related)

- **International Energy Agency (IEA)**  
  *World Energy Outlook 2025 – Annex A (Free Dataset)*  
  Scenario-based global CO₂ emissions trajectories:
  - **STEPS** (Stated Policies Scenario – baseline)
  - **NZE** (Net Zero Emissions by 2050)

All data used is **publicly available**.

---

## 🔍 Scope & Assumptions

To ensure rigor and defensibility, the analysis is deliberately scoped:

- **Geography**: World only  
- **Gas**: CO₂ only (energy-related)  
- **Time horizon**:
  - Historical: 1990–2023
  - Scenarios: up to 2050
- **Methodology**: scenario comparison (no forecasting, no causal claims)

These limitations are explicit by design and strengthen interpretability.

---

## Project Structure

```text
climate-scenario-pipeline/
│
├── data/
│   ├── raw/            # Original datasets (OWID, IEA)
│   ├── interim/        # Intermediate artifacts (optional)
│   └── processed/      # Analysis-ready tables
│
├── outputs/
│   ├── figures/        # Generated plots
│   └── tables/         # Exported analysis tables
│
├── src/
│   ├── config.py       # Central configuration & constants
│   ├── io.py           # Raw data loaders
│   ├── processing.py  # Data harmonization & canonical schema
│   ├── scenarios.py   # Scenario analysis logic
│   ├── visualization.py # Publication-grade figures
│   ├── utils.py       # Minimal shared utilities
│
├── main.py             # Single execution point
├── requirements.txt
└── README.md
```

## Reproducibility

The entire pipeline is executed from a single command:

```
python main.py
```

This will:

	1.	Load raw datasets
	2.	Harmonize data into a canonical schema
	3.	Run scenario-based emissions analysis
	4.	Generate and save figures

All results are reproducible end-to-end.

## Outputs 

The pipeline produces:

	•	Emissions trajectories by scenario (historical + baseline vs net zero)

	•	Absolute emissions gap vs baseline (quantifying transition ambition over time)

Figures are saved in : 

```
outputs/figures/
````
and are ready for inclusion in reports or presentations.

## Methodological Notes

•	No machine learning is used in the core pipeline.

•	All transformations and assumptions are explicit.

•	Assertions and schema checks prevent silent data corruption.

•	The architecture cleanly separates :

	•	data loading,
	•	processing,
	•	analysis,
	•	visualization.

This design prioritizes transparency and robustness over complexity.

## Possible Extensions 

The current implementation is intentionally conservative.

Potential extensions include :
```
• sector-level disaggregation (if supported by data),

• sensitivity analysis across additional scenarios,

• carbon price overlays or transition risk metrics.
```
These can be added without modifying the core architecture.

## License & Disclaimer 

This project is for academic and educational purposes only.

It does not produce forecasts, investment advice, or policy recommendations. 

All scenario data is sourced from authoritative public institutions.