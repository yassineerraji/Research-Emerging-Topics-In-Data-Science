"""
Utility Functions Module

Provides helper functions and utilities for the climate scenario pipeline.
"""

import os
import json
import pickle
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path


def load_json_config(filepath: str) -> dict:
    """
    Load configuration from JSON file.
    
    Args:
        filepath (str): Path to JSON file
        
    Returns:
        dict: Configuration dictionary
    """
    with open(filepath, 'r') as f:
        config = json.load(f)
    return config


def save_json_config(config: dict, filepath: str):
    """
    Save configuration to JSON file.
    
    Args:
        config (dict): Configuration dictionary
        filepath (str): Path to save JSON file
    """
    with open(filepath, 'w') as f:
        json.dump(config, f, indent=4)
    print(f"Configuration saved to: {filepath}")


def save_pickle(obj: Any, filepath: str):
    """
    Save object to pickle file.
    
    Args:
        obj: Object to save
        filepath (str): Path to save pickle file
    """
    with open(filepath, 'wb') as f:
        pickle.dump(obj, f)
    print(f"Object saved to: {filepath}")


def load_pickle(filepath: str) -> Any:
    """
    Load object from pickle file.
    
    Args:
        filepath (str): Path to pickle file
        
    Returns:
        Any: Loaded object
    """
    with open(filepath, 'rb') as f:
        obj = pickle.load(f)
    print(f"Object loaded from: {filepath}")
    return obj


def get_timestamp() -> str:
    """
    Get current timestamp as string.
    
    Returns:
        str: Timestamp string (YYYYMMDD_HHMMSS)
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def create_run_directory(base_dir: str, run_name: Optional[str] = None) -> Path:
    """
    Create a timestamped directory for a pipeline run.
    
    Args:
        base_dir (str): Base directory path
        run_name (str): Optional run name
        
    Returns:
        Path: Created directory path
    """
    timestamp = get_timestamp()
    
    if run_name:
        dir_name = f"{run_name}_{timestamp}"
    else:
        dir_name = f"run_{timestamp}"
    
    run_dir = Path(base_dir) / dir_name
    run_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Created run directory: {run_dir}")
    return run_dir


def log_pipeline_step(step_name: str, status: str = "START", details: Optional[str] = None):
    """
    Log pipeline execution step.
    
    Args:
        step_name (str): Name of the step
        status (str): Status ('START', 'COMPLETE', 'ERROR')
        details (str): Optional details
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"[{timestamp}] {status}: {step_name}"
    
    if details:
        message += f" - {details}"
    
    print(message)


def compute_summary_statistics(data: pd.DataFrame, value_cols: List[str]) -> pd.DataFrame:
    """
    Compute summary statistics for specified columns.
    
    Args:
        data (pd.DataFrame): Input data
        value_cols (list): Columns to summarize
        
    Returns:
        pd.DataFrame: Summary statistics
    """
    summary = data[value_cols].describe().T
    summary['missing'] = data[value_cols].isnull().sum()
    summary['missing_pct'] = (summary['missing'] / len(data) * 100).round(2)
    
    return summary


def validate_data_structure(data: pd.DataFrame, 
                           required_columns: List[str],
                           raise_error: bool = True) -> bool:
    """
    Validate that dataframe has required columns.
    
    Args:
        data (pd.DataFrame): Data to validate
        required_columns (list): List of required column names
        raise_error (bool): Whether to raise error if validation fails
        
    Returns:
        bool: True if valid, False otherwise
    """
    missing_cols = set(required_columns) - set(data.columns)
    
    if missing_cols:
        message = f"Missing required columns: {missing_cols}"
        if raise_error:
            raise ValueError(message)
        else:
            print(f"Warning: {message}")
            return False
    
    return True


def convert_units(data: pd.DataFrame,
                 column: str,
                 from_unit: str,
                 to_unit: str) -> pd.DataFrame:
    """
    Convert units for a specific column.
    
    Args:
        data (pd.DataFrame): Input data
        column (str): Column to convert
        from_unit (str): Current unit
        to_unit (str): Target unit
        
    Returns:
        pd.DataFrame: Data with converted units
    """
    conversions = {
        ('celsius', 'fahrenheit'): lambda x: x * 9/5 + 32,
        ('fahrenheit', 'celsius'): lambda x: (x - 32) * 5/9,
        ('mm', 'inches'): lambda x: x / 25.4,
        ('inches', 'mm'): lambda x: x * 25.4,
        ('m', 'ft'): lambda x: x * 3.28084,
        ('ft', 'm'): lambda x: x / 3.28084,
    }
    
    key = (from_unit.lower(), to_unit.lower())
    
    if key not in conversions:
        raise ValueError(f"Conversion from {from_unit} to {to_unit} not supported")
    
    data[column] = conversions[key](data[column])
    print(f"Converted {column} from {from_unit} to {to_unit}")
    
    return data


def filter_date_range(data: pd.DataFrame,
                     datetime_col: str,
                     start_date: Optional[str] = None,
                     end_date: Optional[str] = None) -> pd.DataFrame:
    """
    Filter dataframe to a specific date range.
    
    Args:
        data (pd.DataFrame): Input data
        datetime_col (str): Datetime column name
        start_date (str): Start date (YYYY-MM-DD)
        end_date (str): End date (YYYY-MM-DD)
        
    Returns:
        pd.DataFrame: Filtered data
    """
    data[datetime_col] = pd.to_datetime(data[datetime_col])
    
    if start_date:
        data = data[data[datetime_col] >= pd.to_datetime(start_date)]
        print(f"Filtered to dates >= {start_date}")
    
    if end_date:
        data = data[data[datetime_col] <= pd.to_datetime(end_date)]
        print(f"Filtered to dates <= {end_date}")
    
    print(f"Filtered data shape: {data.shape}")
    return data


def export_results_summary(results: Dict[str, Any], 
                          output_path: str,
                          format: str = 'json'):
    """
    Export results summary to file.
    
    Args:
        results (dict): Results dictionary
        output_path (str): Output file path
        format (str): Output format ('json', 'txt')
    """
    if format == 'json':
        # Convert non-serializable objects
        serializable_results = {}
        for key, value in results.items():
            if isinstance(value, (pd.DataFrame, pd.Series)):
                serializable_results[key] = value.to_dict()
            elif isinstance(value, np.ndarray):
                serializable_results[key] = value.tolist()
            elif isinstance(value, (np.integer, np.floating)):
                serializable_results[key] = value.item()
            else:
                serializable_results[key] = str(value)
        
        with open(output_path, 'w') as f:
            json.dump(serializable_results, f, indent=4)
    
    elif format == 'txt':
        with open(output_path, 'w') as f:
            f.write("Results Summary\n")
            f.write("=" * 60 + "\n\n")
            for key, value in results.items():
                f.write(f"{key}:\n{value}\n\n")
    
    print(f"Results summary exported to: {output_path}")


def check_data_quality(data: pd.DataFrame) -> Dict[str, Any]:
    """
    Perform data quality checks.
    
    Args:
        data (pd.DataFrame): Data to check
        
    Returns:
        dict: Quality report
    """
    report = {
        'shape': data.shape,
        'columns': list(data.columns),
        'dtypes': data.dtypes.to_dict(),
        'missing_values': data.isnull().sum().to_dict(),
        'duplicate_rows': data.duplicated().sum(),
        'memory_usage_mb': data.memory_usage(deep=True).sum() / 1024**2
    }
    
    print("Data Quality Report:")
    print(f"  Shape: {report['shape']}")
    print(f"  Duplicate rows: {report['duplicate_rows']}")
    print(f"  Memory usage: {report['memory_usage_mb']:.2f} MB")
    print(f"  Columns with missing values: {sum(1 for v in report['missing_values'].values() if v > 0)}")
    
    return report


if __name__ == "__main__":
    print("Utils module loaded.")
    print("Available functions: save_pickle, load_pickle, compute_summary_statistics, etc.")
