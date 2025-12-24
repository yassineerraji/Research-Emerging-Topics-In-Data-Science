"""
ml_analysis.py

Machine Learning extension for the climate scenario analysis pipeline.

Purpose
-------
This module provides an *interpretation* layer on top of scenario trajectories.
It does NOT forecast emissions and does NOT alter the scenario data.

We use unsupervised learning (K-Means) to identify "decarbonization regimes"
based on interpretable, engineered features derived from emissions trajectories
(e.g., year-on-year change, acceleration, indexed level).

Outputs
-------
- Feature table per (scenario, year)
- Cluster assignments per (scenario, year)

All logic is deterministic given a fixed random_state.
"""

from __future__ import annotations

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from src.config import BASELINE_SCENARIO, NET_ZERO_SCENARIO


def build_ml_features(
    trajectories: pd.DataFrame,
    start_year: int = 2020,
) -> pd.DataFrame:
    """
    Build an ML-ready feature table from annual emissions trajectories.

    We deliberately engineer interpretable features rather than feeding raw
    emissions blindly.

    Parameters
    ----------
    trajectories : pd.DataFrame
        DataFrame with columns: ['year', 'scenario', 'value'].
    start_year : int
        First year to include in the ML feature space (default: 2020).

    Returns
    -------
    pd.DataFrame
        Feature table with one row per (scenario, year).
    """
    # Focus on scenarios we analyze (exclude historical for the ML extension)
    df = trajectories[trajectories["scenario"].isin([BASELINE_SCENARIO, NET_ZERO_SCENARIO])].copy()

    # Keep a modern window where scenario divergence is meaningful
    df = df[df["year"] >= start_year].copy()

    # Ensure correct sorting for time-difference features
    df = df.sort_values(["scenario", "year"]).reset_index(drop=True)

    # Compute "indexed" level (Index = 100 at first year of each scenario)
    df["value_base"] = df.groupby("scenario")["value"].transform("first")
    df["emissions_index"] = (df["value"] / df["value_base"]) * 100

    # Year-over-year (YoY) absolute change in emissions
    df["delta_abs"] = df.groupby("scenario")["value"].diff()

    # YoY percent change (careful with near-zero values)
    # We use pct_change on the raw series; interpret as relative rate of change.
    df["delta_pct"] = df.groupby("scenario")["value"].pct_change() * 100

    # Second difference: acceleration (change in the change)
    df["accel_abs"] = df.groupby("scenario")["delta_abs"].diff()

    # Drop early rows where diffs are undefined
    # (first year has no delta; second year has no acceleration)
    df = df.dropna(subset=["delta_abs", "delta_pct", "accel_abs"]).copy()

    # Select final feature columns (interpretable, compact)
    features = df[
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

    return features


def cluster_decarbonization_regimes(
    features_df: pd.DataFrame,
    k: int = 3,
    random_state: int = 42,
) -> pd.DataFrame:
    """
    Cluster trajectory points into decarbonization regimes using K-Means.

    This clustering is an *interpretation tool*:
    - It identifies patterns in rates/acceleration of change
    - It does not claim causality
    - It does not predict future values

    Parameters
    ----------
    features_df : pd.DataFrame
        Output of build_ml_features().
    k : int
        Number of clusters/regimes (default: 3).
    random_state : int
        Seed for determinism.

    Returns
    -------
    pd.DataFrame
        Copy of features_df with an added 'cluster' column.
    """
    df = features_df.copy()

    # Feature matrix for clustering
    X = df[["emissions_index", "delta_abs", "delta_pct", "accel_abs"]].values

    # Standardize features to prevent scale dominance (required for K-Means)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # K-Means clustering (deterministic with random_state)
    model = KMeans(n_clusters=k, random_state=random_state, n_init=10)
    df["cluster"] = model.fit_predict(X_scaled)

    return df