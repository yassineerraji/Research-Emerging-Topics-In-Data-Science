"""
utils.py

General-purpose utility functions for the climate scenario analysis pipeline.

This module contains small, reusable helpers that are:
- domain-agnostic
- shared across multiple modules
- intentionally minimal

It must not contain any data processing, scenario logic, or visualization code.
"""

from pathlib import Path
import pandas as pd


def log_step(message: str) -> None:
    """
    Print a standardized log message for pipeline steps.

    Parameters
    ----------
    message : str
        Description of the pipeline step being executed.
    """
    print(f"[INFO] {message}")


def save_dataframe(
    df: pd.DataFrame,
    path: Path,
    index: bool = False,
) -> None:
    """
    Save a pandas DataFrame to disk as a CSV file.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to save.
    path : Path
        Destination file path.
    index : bool, optional
        Whether to include the index in the saved file, by default False.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=index)


def assert_canonical_schema(
    df: pd.DataFrame,
    expected_columns: list[str],
) -> None:
    """
    Assert that a DataFrame matches the expected canonical schema.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to validate.
    expected_columns : list of str
        List of expected column names.

    Raises
    ------
    AssertionError
        If the DataFrame does not match the expected schema.
    """
    missing = set(expected_columns) - set(df.columns)
    extra = set(df.columns) - set(expected_columns)

    if missing or extra:
        raise AssertionError(
            f"Schema mismatch. Missing: {missing}, Extra: {extra}"
        )