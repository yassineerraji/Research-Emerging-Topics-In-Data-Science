# Business Presentation (7–10 slides) — Outline

## Slide 1 — Title
- Reproducible Climate Scenario \& Transition Risk Pipeline
- World CO₂ (OWID) + IEA WEO 2025 scenarios (STEPS vs NZE)
- Role: Climate Data Scientist / Climate Analytics Engineer

## Slide 2 — Problem \& value proposition
- Teams need fast, repeatable scenario comparisons and risk signals
- Manual spreadsheets don’t scale and are hard to audit
- Value: a production-like pipeline that reproduces all results in one command

## Slide 3 — Data sources (trusted, public)
- OWID: historical global CO₂ (1990–2023)
- IEA WEO 2025 Annex A: scenario pathways + sector (FLOW) breakdown
- Guardrails: strict series selection to prevent double counting

## Slide 4 — Architecture (end-to-end workflow)
- Ingest → validate → canonicalize → scenario metrics → risk layer → figures/tables
- Modular Python (`src/processing.py`, `src/scenarios.py`, `src/risk.py`, `src/visualization.py`)
- Single entry point: `python main.py`

## Slide 5 — Scenario analytics (what we compute)
- Annualized trajectories (explicit interpolation)
- Gap vs baseline (absolute and %)
- Cumulative emissions (annualized)
- Indexed trajectories (relative change)

## Slide 6 — Sector insights (IEA FLOW)
- Industry / Transport / Buildings / Power sector inputs / Other energy
- Grid plot and sector tables enable drill-down
- Supports targeted transition discussions (which sectors drive the gap?)

## Slide 7 — Transition risk proxy (carbon cost stress test)
- Carbon cost = emissions × carbon price (USD/tCO₂)
- Scenario-dependent price paths (stylized, configurable)
- Outputs: annual cost + cumulative cost by sector and scenario

## Slide 8 — Reproducibility \& governance
- Pinned dependencies (`requirements.txt`)
- Run metadata (`run_metadata.json`)
- Unit tests + CI (GitHub Actions)
- Deterministic results (seeded ML when enabled)

## Slide 9 — Demo (what the stakeholder gets)
- One command run → refreshed figures/tables for report & slides
- Clear outputs folder structure
- Ready to extend to entity-level exposures

## Slide 10 — Next steps
- Add more IEA scenarios (APS, CPS) and sensitivity runs
- Entity mapping (sector → company) and financial exposure model
- Improved annualization if higher-frequency scenario data is available


