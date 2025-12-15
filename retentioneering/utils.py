"""
Utility functions shared across the toolkit.
"""

import pandas as pd
import numpy as np
from retentioneering.constants import COL_USER_ID, COL_EVENT, COL_TIMESTAMP


def validate_dataframe(df: pd.DataFrame) -> None:
    """Check that the dataframe has the required columns."""
    required = {COL_USER_ID, COL_EVENT, COL_TIMESTAMP}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"DataFrame is missing required columns: {missing}")


def sort_events(df: pd.DataFrame) -> pd.DataFrame:
    """Sort event log by user and timestamp."""
    return df.sort_values([COL_USER_ID, COL_TIMESTAMP]).reset_index(drop=True)


def get_user_paths(df: pd.DataFrame) -> dict:
    """
    Group events by user and return a dict of {user_id: [event_list]}.
    Assumes data is already sorted by timestamp.
    """
    df_sorted = sort_events(df)
    return df_sorted.groupby(COL_USER_ID)[COL_EVENT].apply(list).to_dict()


def to_datetime(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure the timestamp column is datetime type."""
    df = df.copy()
    df[COL_TIMESTAMP] = pd.to_datetime(df[COL_TIMESTAMP])
    return df


def get_first_events(df: pd.DataFrame) -> pd.DataFrame:
    """Get the first event per user."""
    df_sorted = sort_events(df)
    return df_sorted.groupby(COL_USER_ID).first().reset_index()


def get_last_events(df: pd.DataFrame) -> pd.DataFrame:
    """Get the last event per user."""
    df_sorted = sort_events(df)
    return df_sorted.groupby(COL_USER_ID).last().reset_index()


def count_unique_users(df: pd.DataFrame) -> int:
    """Return the number of unique users."""
    return df[COL_USER_ID].nunique()


def event_frequency(df: pd.DataFrame) -> pd.Series:
    """Return event counts sorted descending."""
    return df[COL_EVENT].value_counts()
