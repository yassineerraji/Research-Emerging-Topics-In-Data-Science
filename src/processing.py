"""
Data Processing Module

Handles data cleaning, harmonization, and transformation operations.
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Tuple
from sklearn.preprocessing import StandardScaler
from . import config


def clean_missing_values(data: pd.DataFrame, 
                        strategy: str = 'mean',
                        threshold: float = 0.5) -> pd.DataFrame:
    """
    Clean missing values in the dataset.
    
    Args:
        data (pd.DataFrame): Input data
        strategy (str): Strategy for handling missing values ('mean', 'median', 'drop', 'forward_fill')
        threshold (float): Drop columns with more than this proportion of missing values
        
    Returns:
        pd.DataFrame: Cleaned data
    """
    print("Cleaning missing values...")
    print(f"Initial missing values:\n{data.isnull().sum()[data.isnull().sum() > 0]}")
    
    # Drop columns with too many missing values
    missing_ratio = data.isnull().sum() / len(data)
    cols_to_drop = missing_ratio[missing_ratio > threshold].index.tolist()
    
    if cols_to_drop:
        print(f"Dropping columns with >{threshold*100}% missing: {cols_to_drop}")
        data = data.drop(columns=cols_to_drop)
    
    # Handle remaining missing values
    if strategy == 'mean':
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        data[numeric_cols] = data[numeric_cols].fillna(data[numeric_cols].mean())
    elif strategy == 'median':
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        data[numeric_cols] = data[numeric_cols].fillna(data[numeric_cols].median())
    elif strategy == 'forward_fill':
        data = data.fillna(method='ffill')
    elif strategy == 'drop':
        data = data.dropna()
    
    print(f"Cleaned data shape: {data.shape}")
    return data


def remove_outliers(data: pd.DataFrame, 
                   columns: Optional[List[str]] = None,
                   threshold: float = 3.0) -> pd.DataFrame:
    """
    Remove outliers using z-score method.
    
    Args:
        data (pd.DataFrame): Input data
        columns (List[str]): Columns to check for outliers (None = all numeric)
        threshold (float): Z-score threshold for outlier detection
        
    Returns:
        pd.DataFrame: Data with outliers removed
    """
    print(f"Removing outliers (threshold: {threshold} std)...")
    
    if columns is None:
        columns = data.select_dtypes(include=[np.number]).columns.tolist()
    
    initial_rows = len(data)
    
    for col in columns:
        z_scores = np.abs((data[col] - data[col].mean()) / data[col].std())
        data = data[z_scores < threshold]
    
    removed = initial_rows - len(data)
    print(f"Removed {removed} outlier rows ({removed/initial_rows*100:.2f}%)")
    
    return data


def harmonize_datetime(data: pd.DataFrame, 
                      datetime_col: str,
                      freq: str = 'D') -> pd.DataFrame:
    """
    Harmonize datetime column to consistent format and frequency.
    
    Args:
        data (pd.DataFrame): Input data
        datetime_col (str): Name of datetime column
        freq (str): Target frequency ('D'=daily, 'M'=monthly, 'Y'=yearly)
        
    Returns:
        pd.DataFrame: Data with harmonized datetime
    """
    print(f"Harmonizing datetime column: {datetime_col}")
    
    # Convert to datetime
    data[datetime_col] = pd.to_datetime(data[datetime_col])
    
    # Set as index for resampling
    data = data.set_index(datetime_col)
    
    # Resample to target frequency
    numeric_cols = data.select_dtypes(include=[np.number]).columns
    data = data[numeric_cols].resample(freq).mean()
    
    # Reset index
    data = data.reset_index()
    
    print(f"Harmonized to {freq} frequency. Shape: {data.shape}")
    return data


def normalize_spatial_units(data: pd.DataFrame,
                           region_col: str,
                           region_mapping: Optional[dict] = None) -> pd.DataFrame:
    """
    Normalize spatial units to consistent regions.
    
    Args:
        data (pd.DataFrame): Input data
        region_col (str): Name of region/location column
        region_mapping (dict): Mapping from original to standardized region names
        
    Returns:
        pd.DataFrame: Data with normalized regions
    """
    print("Normalizing spatial units...")
    
    if region_mapping:
        data[region_col] = data[region_col].replace(region_mapping)
        print(f"Applied region mapping with {len(region_mapping)} mappings")
    
    # Standardize region names (strip whitespace, title case)
    data[region_col] = data[region_col].str.strip().str.title()
    
    print(f"Unique regions: {data[region_col].nunique()}")
    return data


def create_features(data: pd.DataFrame,
                   datetime_col: Optional[str] = None) -> pd.DataFrame:
    """
    Create additional features from existing data.
    
    Args:
        data (pd.DataFrame): Input data
        datetime_col (str): Name of datetime column for temporal features
        
    Returns:
        pd.DataFrame: Data with additional features
    """
    print("Creating additional features...")
    
    # Temporal features
    if datetime_col and datetime_col in data.columns:
        data[datetime_col] = pd.to_datetime(data[datetime_col])
        data['year'] = data[datetime_col].dt.year
        data['month'] = data[datetime_col].dt.month
        data['quarter'] = data[datetime_col].dt.quarter
        data['day_of_year'] = data[datetime_col].dt.dayofyear
        print("Added temporal features: year, month, quarter, day_of_year")
    
    # Interaction features (example for climate data)
    if 'temperature' in data.columns and 'precipitation' in data.columns:
        data['temp_precip_interaction'] = data['temperature'] * data['precipitation']
        print("Added interaction feature: temp_precip_interaction")
    
    # Rolling statistics (if time series)
    numeric_cols = data.select_dtypes(include=[np.number]).columns
    for col in numeric_cols[:3]:  # Limit to first 3 numeric columns
        if len(data) > 30:
            data[f'{col}_rolling_30d'] = data[col].rolling(window=30, min_periods=1).mean()
            print(f"Added rolling feature: {col}_rolling_30d")
    
    return data


def aggregate_to_baseline(data: pd.DataFrame,
                         datetime_col: str,
                         baseline_years: Tuple[int, int],
                         value_cols: List[str]) -> pd.DataFrame:
    """
    Aggregate data to baseline period statistics.
    
    Args:
        data (pd.DataFrame): Input data
        datetime_col (str): Name of datetime column
        baseline_years (tuple): Start and end years for baseline (e.g., (1981, 2010))
        value_cols (list): Columns to aggregate
        
    Returns:
        pd.DataFrame: Baseline statistics
    """
    print(f"Computing baseline statistics for {baseline_years[0]}-{baseline_years[1]}...")
    
    data[datetime_col] = pd.to_datetime(data[datetime_col])
    data['year'] = data[datetime_col].dt.year
    
    # Filter to baseline period
    baseline_data = data[
        (data['year'] >= baseline_years[0]) & 
        (data['year'] <= baseline_years[1])
    ]
    
    # Compute statistics
    baseline_stats = {}
    for col in value_cols:
        baseline_stats[f'{col}_baseline_mean'] = baseline_data[col].mean()
        baseline_stats[f'{col}_baseline_std'] = baseline_data[col].std()
    
    print(f"Baseline statistics computed for {len(value_cols)} variables")
    return pd.DataFrame([baseline_stats])


def prepare_modeling_data(data: pd.DataFrame,
                        target_col: str,
                        feature_cols: Optional[List[str]] = None,
                        scale: bool = True) -> dict:
    """
    Prepare data for modeling.
    
    Args:
        data (pd.DataFrame): Input data
        target_col (str): Target variable column
        feature_cols (list): Feature columns (None = all except target)
        scale (bool): Whether to scale features
        
    Returns:
        dict: Dictionary with X, y, feature_names, and scaler
    """
    print("Preparing data for modeling...")
    
    # Separate features and target
    if feature_cols is None:
        feature_cols = [col for col in data.columns if col != target_col]
    
    X = data[feature_cols].select_dtypes(include=[np.number])
    y = data[target_col]
    
    # Scale features
    scaler = None
    if scale:
        scaler = StandardScaler()
        X = pd.DataFrame(
            scaler.fit_transform(X),
            columns=X.columns,
            index=X.index
        )
        print("Features scaled using StandardScaler")
    
    print(f"Features shape: {X.shape}")
    print(f"Target shape: {y.shape}")
    
    return {
        'X': X,
        'y': y,
        'feature_names': X.columns.tolist(),
        'scaler': scaler
    }


if __name__ == "__main__":
    print("Processing module loaded.")
    print("Available functions: clean_missing_values, remove_outliers, harmonize_datetime, etc.")
