"""
Climate Scenarios Module

Handles scenario extraction, analysis, and projection runs.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from . import config


def extract_scenario_data(data: pd.DataFrame,
                         scenario_col: str,
                         scenario_name: str) -> pd.DataFrame:
    """
    Extract data for a specific scenario.
    
    Args:
        data (pd.DataFrame): Input data with scenarios
        scenario_col (str): Name of scenario column
        scenario_name (str): Scenario identifier (e.g., 'RCP4.5')
        
    Returns:
        pd.DataFrame: Data filtered to the specified scenario
    """
    print(f"Extracting scenario: {scenario_name}")
    
    scenario_data = data[data[scenario_col] == scenario_name].copy()
    
    print(f"Extracted {len(scenario_data)} records for {scenario_name}")
    return scenario_data


def compute_anomalies(data: pd.DataFrame,
                     value_col: str,
                     baseline_mean: float,
                     datetime_col: Optional[str] = None) -> pd.DataFrame:
    """
    Compute anomalies relative to baseline.
    
    Args:
        data (pd.DataFrame): Input data
        value_col (str): Column to compute anomalies for
        baseline_mean (float): Baseline mean value
        datetime_col (str): Datetime column for temporal context
        
    Returns:
        pd.DataFrame: Data with anomaly column added
    """
    print(f"Computing anomalies for {value_col} (baseline: {baseline_mean:.2f})")
    
    data[f'{value_col}_anomaly'] = data[value_col] - baseline_mean
    
    if datetime_col and datetime_col in data.columns:
        # Compute moving average of anomalies
        data[f'{value_col}_anomaly_ma'] = data[f'{value_col}_anomaly'].rolling(
            window=12, min_periods=1
        ).mean()
    
    print(f"Mean anomaly: {data[f'{value_col}_anomaly'].mean():.2f}")
    return data


def project_trends(data: pd.DataFrame,
                  datetime_col: str,
                  value_cols: List[str],
                  projection_years: List[int],
                  method: str = 'linear') -> pd.DataFrame:
    """
    Project future trends based on historical data.
    
    Args:
        data (pd.DataFrame): Historical data
        datetime_col (str): Datetime column
        value_cols (list): Variables to project
        projection_years (list): Years to project into
        method (str): Projection method ('linear', 'polynomial')
        
    Returns:
        pd.DataFrame: Projected data
    """
    print(f"Projecting trends using {method} method...")
    
    data[datetime_col] = pd.to_datetime(data[datetime_col])
    data['year'] = data[datetime_col].dt.year
    
    # Prepare training data
    X_train = data['year'].values.reshape(-1, 1)
    
    projections = []
    
    for year in projection_years:
        projection = {'year': year}
        
        for col in value_cols:
            if col not in data.columns:
                continue
                
            y_train = data[col].values
            
            # Fit model
            if method == 'linear':
                model = LinearRegression()
            else:
                from sklearn.preprocessing import PolynomialFeatures
                poly = PolynomialFeatures(degree=2)
                X_train_poly = poly.fit_transform(X_train)
                model = LinearRegression()
                X_train_poly_fit = X_train_poly
                model.fit(X_train_poly_fit, y_train)
                X_pred = poly.transform([[year]])
                projection[col] = model.predict(X_pred)[0]
                continue
            
            model.fit(X_train, y_train)
            
            # Make projection
            y_pred = model.predict([[year]])
            projection[col] = y_pred[0]
        
        projections.append(projection)
    
    projection_df = pd.DataFrame(projections)
    print(f"Projected {len(value_cols)} variables to {len(projection_years)} years")
    
    return projection_df


def run_scenario_analysis(data: pd.DataFrame,
                         scenarios: List[str],
                         scenario_col: str,
                         value_col: str,
                         datetime_col: str) -> pd.DataFrame:
    """
    Run comparative analysis across multiple scenarios.
    
    Args:
        data (pd.DataFrame): Input data with multiple scenarios
        scenarios (list): List of scenario identifiers
        scenario_col (str): Name of scenario column
        value_col (str): Variable to analyze
        datetime_col (str): Datetime column
        
    Returns:
        pd.DataFrame: Summary statistics by scenario
    """
    print(f"Running scenario analysis for: {scenarios}")
    
    data[datetime_col] = pd.to_datetime(data[datetime_col])
    data['year'] = data[datetime_col].dt.year
    
    results = []
    
    for scenario in scenarios:
        scenario_data = data[data[scenario_col] == scenario]
        
        if len(scenario_data) == 0:
            print(f"Warning: No data found for scenario {scenario}")
            continue
        
        # Compute statistics
        stats = {
            'scenario': scenario,
            f'{value_col}_mean': scenario_data[value_col].mean(),
            f'{value_col}_std': scenario_data[value_col].std(),
            f'{value_col}_min': scenario_data[value_col].min(),
            f'{value_col}_max': scenario_data[value_col].max(),
            f'{value_col}_2050': scenario_data[
                scenario_data['year'] == 2050
            ][value_col].mean() if 2050 in scenario_data['year'].values else np.nan,
            f'{value_col}_2100': scenario_data[
                scenario_data['year'] == 2100
            ][value_col].mean() if 2100 in scenario_data['year'].values else np.nan,
        }
        
        results.append(stats)
    
    results_df = pd.DataFrame(results)
    print(f"\nScenario Analysis Summary:")
    print(results_df)
    
    return results_df


def compute_scenario_divergence(data: pd.DataFrame,
                               scenarios: List[str],
                               scenario_col: str,
                               value_col: str,
                               datetime_col: str,
                               reference_year: int = 2020) -> pd.DataFrame:
    """
    Compute how scenarios diverge over time from a reference year.
    
    Args:
        data (pd.DataFrame): Input data
        scenarios (list): List of scenario identifiers
        scenario_col (str): Name of scenario column
        value_col (str): Variable to analyze
        datetime_col (str): Datetime column
        reference_year (int): Reference year for computing divergence
        
    Returns:
        pd.DataFrame: Divergence metrics
    """
    print(f"Computing scenario divergence from {reference_year}...")
    
    data[datetime_col] = pd.to_datetime(data[datetime_col])
    data['year'] = data[datetime_col].dt.year
    
    # Get reference values
    reference_values = {}
    for scenario in scenarios:
        ref_data = data[
            (data[scenario_col] == scenario) & 
            (data['year'] == reference_year)
        ]
        if len(ref_data) > 0:
            reference_values[scenario] = ref_data[value_col].mean()
    
    # Compute divergence for each year
    years = sorted(data['year'].unique())
    divergence_data = []
    
    for year in years:
        if year < reference_year:
            continue
            
        year_data = {'year': year}
        
        for scenario in scenarios:
            scenario_year_data = data[
                (data[scenario_col] == scenario) & 
                (data['year'] == year)
            ]
            
            if len(scenario_year_data) > 0 and scenario in reference_values:
                current_value = scenario_year_data[value_col].mean()
                divergence = current_value - reference_values[scenario]
                year_data[f'{scenario}_divergence'] = divergence
        
        divergence_data.append(year_data)
    
    divergence_df = pd.DataFrame(divergence_data)
    print(f"Computed divergence for {len(years)} years")
    
    return divergence_df


def ensemble_scenarios(scenario_projections: Dict[str, pd.DataFrame],
                      value_col: str,
                      weights: Optional[Dict[str, float]] = None) -> pd.DataFrame:
    """
    Create ensemble projection from multiple scenarios.
    
    Args:
        scenario_projections (dict): Dictionary of {scenario_name: projection_df}
        value_col (str): Variable to ensemble
        weights (dict): Optional weights for each scenario
        
    Returns:
        pd.DataFrame: Ensemble projection
    """
    print("Creating ensemble projection...")
    
    if weights is None:
        weights = {scenario: 1.0/len(scenario_projections) 
                  for scenario in scenario_projections}
    
    # Ensure weights sum to 1
    weight_sum = sum(weights.values())
    weights = {k: v/weight_sum for k, v in weights.items()}
    
    # Combine scenarios
    ensemble = None
    
    for scenario, proj_df in scenario_projections.items():
        weight = weights.get(scenario, 0)
        
        if ensemble is None:
            ensemble = proj_df[['year']].copy()
            ensemble[value_col] = proj_df[value_col] * weight
        else:
            ensemble[value_col] += proj_df[value_col] * weight
    
    print(f"Created ensemble from {len(scenario_projections)} scenarios")
    return ensemble


if __name__ == "__main__":
    print("Scenarios module loaded.")
    print("Available functions: extract_scenario_data, compute_anomalies, project_trends, etc.")
