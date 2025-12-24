"""
Input/Output Module

Handles data downloading, loading, and saving operations.
"""

import os
import pandas as pd
import requests
from pathlib import Path
from typing import Optional, Union
from . import config


def download_data(source_key: str, force_download: bool = False) -> Path:
    """
    Download data from configured sources.
    
    Args:
        source_key (str): Key from DATA_SOURCES config
        force_download (bool): Force re-download if file exists
        
    Returns:
        Path: Path to the downloaded file
    """
    if source_key not in config.DATA_SOURCES:
        raise ValueError(f"Unknown data source: {source_key}")
    
    source = config.DATA_SOURCES[source_key]
    output_path = config.RAW_DATA_DIR / source['filename']
    
    if output_path.exists() and not force_download:
        print(f"File already exists: {output_path}")
        return output_path
    
    print(f"Downloading {source['description']}...")
    print(f"URL: {source['url']}")
    
    try:
        response = requests.get(source['url'], stream=True)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Downloaded successfully to: {output_path}")
        return output_path
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading data: {e}")
        raise


def load_raw_data(filename: str) -> pd.DataFrame:
    """
    Load raw data from the raw data directory.
    
    Args:
        filename (str): Name of the file to load
        
    Returns:
        pd.DataFrame: Loaded data
    """
    filepath = config.RAW_DATA_DIR / filename
    
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    print(f"Loading raw data from: {filepath}")
    
    # Determine file type and load accordingly
    if filepath.suffix == '.csv':
        data = pd.read_csv(filepath)
    elif filepath.suffix in ['.xlsx', '.xls']:
        data = pd.read_excel(filepath)
    elif filepath.suffix == '.json':
        data = pd.read_json(filepath)
    elif filepath.suffix == '.parquet':
        data = pd.read_parquet(filepath)
    else:
        raise ValueError(f"Unsupported file format: {filepath.suffix}")
    
    print(f"Loaded data shape: {data.shape}")
    return data


def load_interim_data(filename: str) -> pd.DataFrame:
    """
    Load interim (partially processed) data.
    
    Args:
        filename (str): Name of the file to load
        
    Returns:
        pd.DataFrame: Loaded data
    """
    filepath = config.INTERIM_DATA_DIR / filename
    
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    print(f"Loading interim data from: {filepath}")
    data = pd.read_csv(filepath)
    print(f"Loaded data shape: {data.shape}")
    return data


def load_processed_data(filename: str) -> pd.DataFrame:
    """
    Load processed (final) data ready for modeling.
    
    Args:
        filename (str): Name of the file to load
        
    Returns:
        pd.DataFrame: Loaded data
    """
    filepath = config.PROCESSED_DATA_DIR / filename
    
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    print(f"Loading processed data from: {filepath}")
    data = pd.read_csv(filepath)
    print(f"Loaded data shape: {data.shape}")
    return data


def save_interim_data(data: pd.DataFrame, filename: str) -> Path:
    """
    Save interim data to the interim directory.
    
    Args:
        data (pd.DataFrame): Data to save
        filename (str): Name for the output file
        
    Returns:
        Path: Path to the saved file
    """
    filepath = config.INTERIM_DATA_DIR / filename
    print(f"Saving interim data to: {filepath}")
    data.to_csv(filepath, index=False)
    print(f"Saved successfully. Shape: {data.shape}")
    return filepath


def save_processed_data(data: pd.DataFrame, filename: str) -> Path:
    """
    Save processed data to the processed directory.
    
    Args:
        data (pd.DataFrame): Data to save
        filename (str): Name for the output file
        
    Returns:
        Path: Path to the saved file
    """
    filepath = config.PROCESSED_DATA_DIR / filename
    print(f"Saving processed data to: {filepath}")
    data.to_csv(filepath, index=False)
    print(f"Saved successfully. Shape: {data.shape}")
    return filepath


def save_table(data: pd.DataFrame, filename: str, format: str = 'csv') -> Path:
    """
    Save output tables.
    
    Args:
        data (pd.DataFrame): Data to save
        filename (str): Name for the output file
        format (str): Output format ('csv', 'xlsx', 'latex', 'markdown')
        
    Returns:
        Path: Path to the saved file
    """
    if not filename.endswith(f'.{format}'):
        filename = f"{filename}.{format}"
    
    filepath = config.TABLES_DIR / filename
    print(f"Saving table to: {filepath}")
    
    if format == 'csv':
        data.to_csv(filepath, index=False)
    elif format == 'xlsx':
        data.to_excel(filepath, index=False)
    elif format == 'latex':
        with open(filepath, 'w') as f:
            f.write(data.to_latex(index=False))
    elif format == 'markdown':
        with open(filepath, 'w') as f:
            f.write(data.to_markdown(index=False))
    else:
        raise ValueError(f"Unsupported format: {format}")
    
    print(f"Table saved successfully!")
    return filepath


def list_data_files(directory: str = 'raw') -> list:
    """
    List all data files in a directory.
    
    Args:
        directory (str): Directory to list ('raw', 'interim', 'processed')
        
    Returns:
        list: List of file paths
    """
    dir_map = {
        'raw': config.RAW_DATA_DIR,
        'interim': config.INTERIM_DATA_DIR,
        'processed': config.PROCESSED_DATA_DIR
    }
    
    if directory not in dir_map:
        raise ValueError(f"Unknown directory: {directory}")
    
    target_dir = dir_map[directory]
    files = list(target_dir.glob('*'))
    files = [f for f in files if f.is_file()]
    
    print(f"Files in {directory} directory:")
    for f in files:
        print(f"  - {f.name}")
    
    return files


if __name__ == "__main__":
    print("I/O module loaded.")
    print("Available functions: download_data, load_raw_data, save_interim_data, etc.")
