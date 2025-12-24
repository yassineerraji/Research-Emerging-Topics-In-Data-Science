"""
ml_analysis.py

Machine Learning extension for the climate scenario analysis pipeline.

This module provides TWO ML components:

(A) Global regime clustering (lightweight, illustrative)
    - Clusters (scenario, year) points based on engineered dynamic features.
    - Useful as a conceptual add-on but limited by sample size at global level.

(B) Country-level regime clustering (recommended, substantive)
    - Uses OWID country-level historical CO2 and macro covariates.
    - Builds interpretable features describing decarbonization dynamics.
    - Clusters countries into "historical transition regimes".
    - Provides PCA coordinates for a dense and meaningful visualization.

This ML work is NOT forecasting emissions and does NOT alter scenario trajectories.
It is an interpretation layer meant to enrich the analysis.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from src.config import BASELINE_SCENARIO, NET_ZERO_SCENARIO


# ---------------------------------------------------------------------
# (A) Global ML (illustrative) - kept for completeness
# ---------------------------------------------------------------------
def build_ml_features(
    trajectories: pd.DataFrame,
    start_year: int = 2020,
) -> pd.DataFrame:
    """
    Build an ML-ready feature table from annual global scenario trajectories.

    Parameters
    ----------
    trajectories : pd.DataFrame
        DataFrame with columns: ['year', 'scenario', 'value'].
    start_year : int
        First year to include in the ML feature space.

    Returns
    -------
    pd.DataFrame
        Feature table with one row per (scenario, year).
    """
    df = trajectories[
        trajectories["scenario"].isin([BASELINE_SCENARIO, NET_ZERO_SCENARIO])
    ].copy()

    df = df[df["year"] >= start_year].copy()
    df = df.sort_values(["scenario", "year"]).reset_index(drop=True)

    df["value_base"] = df.groupby("scenario")["value"].transform("first")
    df["emissions_index"] = (df["value"] / df["value_base"]) * 100

    df["delta_abs"] = df.groupby("scenario")["value"].diff()
    df["delta_pct"] = df.groupby("scenario")["value"].pct_change() * 100
    df["accel_abs"] = df.groupby("scenario")["delta_abs"].diff()

    df = df.dropna(subset=["delta_abs", "delta_pct", "accel_abs"]).copy()

    return df[
        [
            "year",
            "scenario",
            "value",
            "emissions_index",
            "delta_abs",
            "delta_pct",
            "accel_abs",
        ]
    ].copy()


def cluster_decarbonization_regimes(
    features_df: pd.DataFrame,
    k: int = 3,
    random_state: int = 42,
) -> pd.DataFrame:
    """
    Cluster global trajectory points into regimes using K-Means.

    This function is robust to small sample sizes:
    - If <2 samples, clustering is skipped (all cluster=0).
    - k is capped to n_samples.

    Returns
    -------
    pd.DataFrame
        features_df with an added 'cluster' column.
    """
    df = features_df.copy()
    n_samples = len(df)

    if n_samples < 2:
        df["cluster"] = 0
        return df

    k_eff = min(k, n_samples)

    X = df[["emissions_index", "delta_abs", "delta_pct", "accel_abs"]].values
    X_scaled = StandardScaler().fit_transform(X)

    model = KMeans(n_clusters=k_eff, random_state=random_state, n_init=10)
    df["cluster"] = model.fit_predict(X_scaled)
    return df


# ---------------------------------------------------------------------
# (B) Country-level ML (substantive)
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class CountryMLConfig:
    """
    Configuration for country-level regime clustering.
    """
    start_year: int = 2010
    end_year: int = 2023
    k: int = 4
    random_state: int = 42
    min_years_required: int = 10


def _is_country_iso(iso_code: str) -> bool:
    """
    Return True if iso_code looks like a real country ISO3 code (not OWID aggregate).
    OWID aggregates often have iso_code starting with 'OWID_'.
    """
    if not isinstance(iso_code, str):
        return False
    if iso_code.startswith("OWID"):
        return False
    return len(iso_code) == 3


def _safe_log(x: pd.Series) -> pd.Series:
    """
    Safe log transform for positive values; returns NaN where x <= 0.
    """
    return np.log(x.where(x > 0))


def _trend_slope(years: np.ndarray, values: np.ndarray) -> float:
    """
    Compute a simple linear trend slope (least squares) for values ~ year.
    Returns NaN if not enough points.
    """
    if len(values) < 2:
        return np.nan
    # polyfit degree 1 returns slope, intercept
    slope, _ = np.polyfit(years.astype(float), values.astype(float), deg=1)
    return float(slope)


def build_country_ml_features(
    owid_raw: pd.DataFrame,
    cfg: CountryMLConfig = CountryMLConfig(),
) -> pd.DataFrame:
    """
    Build country-level ML features from OWID data.

    Features are chosen for interpretability and robustness:
    - emissions_per_capita_level: mean CO2 per capita over window
    - emissions_per_capita_trend: slope of log(CO2 per capita) over window
    - emissions_total_trend: slope of log(total CO2) over window
    - volatility: std of YoY % change in CO2 per capita
    - intensity_level: mean CO2 per GDP over window (if available)
    - income_level: mean GDP per capita over window (if available)

    Parameters
    ----------
    owid_raw : pd.DataFrame
        Raw OWID dataframe containing at least:
        ['iso_code','country','year','co2','co2_per_capita','co2_per_gdp','gdp','population']
        (some may be missing; we handle gracefully)
    cfg : CountryMLConfig
        Configuration.

    Returns
    -------
    pd.DataFrame
        One row per country with engineered features.
    """
    required_cols = {"iso_code", "country", "year", "co2", "co2_per_capita"}
    missing = required_cols - set(owid_raw.columns)
    if missing:
        raise ValueError(f"OWID raw data missing required columns: {sorted(missing)}")

    df = owid_raw.copy()

    # Keep only real countries (exclude OWID aggregates/regions)
    df = df[df["iso_code"].apply(_is_country_iso)].copy()

    # Restrict to the analysis window
    df = df[(df["year"] >= cfg.start_year) & (df["year"] <= cfg.end_year)].copy()

    # Drop rows without core target series
    df = df.dropna(subset=["co2_per_capita"]).copy()

    # Build per-country feature rows
    rows = []
    for iso, g in df.groupby("iso_code"):
        g = g.sort_values("year").copy()

        # Require enough history for stable features
        if g["year"].nunique() < cfg.min_years_required:
            continue

        years = g["year"].to_numpy()

        # Trend on log scale captures multiplicative change
        log_co2pc = _safe_log(g["co2_per_capita"]).to_numpy()
        log_co2 = _safe_log(g["co2"]).to_numpy()

        emissions_per_capita_trend = _trend_slope(years, log_co2pc[~np.isnan(log_co2pc)])
        emissions_total_trend = _trend_slope(years, log_co2[~np.isnan(log_co2)])

        # Volatility: std of YoY % change in CO2 per capita
        yoy_pct = g["co2_per_capita"].pct_change() * 100
        volatility = float(np.nanstd(yoy_pct.to_numpy()))

        # Levels
        emissions_per_capita_level = float(np.nanmean(g["co2_per_capita"].to_numpy()))

        # Optional: intensity and income levels if columns exist
        intensity_level = np.nan
        if "co2_per_gdp" in g.columns:
            intensity_level = float(np.nanmean(g["co2_per_gdp"].to_numpy()))

        income_level = np.nan
        if "gdp" in g.columns and "population" in g.columns:
            gdp_pc = g["gdp"] / g["population"]
            income_level = float(np.nanmean(gdp_pc.to_numpy()))

        country_name = g["country"].iloc[0]

        rows.append(
            {
                "iso_code": iso,
                "country": country_name,
                "start_year": cfg.start_year,
                "end_year": cfg.end_year,
                "years_used": int(g["year"].nunique()),
                "emissions_per_capita_level": emissions_per_capita_level,
                "emissions_per_capita_trend_log": emissions_per_capita_trend,
                "emissions_total_trend_log": emissions_total_trend,
                "volatility_yoy_pct_co2pc": volatility,
                "intensity_level_co2_per_gdp": intensity_level,
                "income_level_gdp_per_capita": income_level,
            }
        )

    features = pd.DataFrame(rows)

    # Drop countries with missing core engineered trends
    features = features.dropna(
        subset=["emissions_per_capita_trend_log", "emissions_total_trend_log"]
    ).copy()

    return features


def cluster_country_regimes(
    country_features: pd.DataFrame,
    cfg: CountryMLConfig = CountryMLConfig(),
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Cluster countries into historical decarbonization regimes and compute PCA coords.

    Returns
    -------
    clustered : pd.DataFrame
        country_features + 'cluster' label
    pca_coords : pd.DataFrame
        iso_code, country, pca1, pca2, cluster (for plotting)
    """
    df = country_features.copy()

    # Select ML feature columns (numeric)
    feature_cols = [
        "emissions_per_capita_level",
        "emissions_per_capita_trend_log",
        "emissions_total_trend_log",
        "volatility_yoy_pct_co2pc",
        "intensity_level_co2_per_gdp",
        "income_level_gdp_per_capita",
    ]

    # Keep only columns that exist (some optional may be fully NaN)
    # Drop columns with all-NaN to avoid scaler errors.
    usable_cols = [c for c in feature_cols if c in df.columns and not df[c].isna().all()]
    X = df[usable_cols].to_numpy(dtype=float)

    # Drop rows with NaNs in usable cols
    mask = ~np.isnan(X).any(axis=1)
    df = df.loc[mask].copy()
    X = X[mask]

    n_samples = X.shape[0]
    if n_samples < 2:
        df["cluster"] = 0
        pca_df = df[["iso_code", "country", "cluster"]].copy()
        pca_df["pca1"] = 0.0
        pca_df["pca2"] = 0.0
        return df, pca_df

    k_eff = min(cfg.k, n_samples)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = KMeans(n_clusters=k_eff, random_state=cfg.random_state, n_init=10)
    df["cluster"] = model.fit_predict(X_scaled)

    # PCA for visualization (2D)
    pca = PCA(n_components=2, random_state=cfg.random_state)
    Z = pca.fit_transform(X_scaled)

    pca_df = df[["iso_code", "country", "cluster"]].copy()
    pca_df["pca1"] = Z[:, 0]
    pca_df["pca2"] = Z[:, 1]

    return df, pca_df