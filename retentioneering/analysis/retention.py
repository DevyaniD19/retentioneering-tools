"""
Retention Analysis - Measure how many users return over time periods.

Computes classic retention: for each user's first-activity period,
what fraction of users are still active N periods later.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from retentioneering.constants import COL_USER_ID, COL_EVENT, COL_TIMESTAMP


class RetentionAnalysis:
    """
    Compute retention rates over time.

    Parameters
    ----------
    eventstream : EventStream
        The event stream to analyze.
    period : str
        Time period granularity: 'D' (day), 'W' (week), 'M' (month).
    max_periods : int
        Maximum number of periods to compute retention for.
    """

    def __init__(self, eventstream, period: str = "W", max_periods: int = 12):
        self.eventstream = eventstream
        self.period = period
        self.max_periods = max_periods
        self._retention_table = self._compute_retention()

    def _compute_retention(self) -> pd.DataFrame:
        """Calculate retention table."""
        df = self.eventstream.df.copy()

        # Assign each event to a period
        df["period"] = df[COL_TIMESTAMP].dt.to_period(self.period)

        # Find each user's first period
        first_period = df.groupby(COL_USER_ID)["period"].min().reset_index()
        first_period.columns = [COL_USER_ID, "cohort_period"]

        # Merge back
        df = df.merge(first_period, on=COL_USER_ID)

        # Compute period offset (how many periods since user's first activity)
        df["period_offset"] = (
            df["period"].apply(lambda x: x.ordinal)
            - df["cohort_period"].apply(lambda x: x.ordinal)
        )

        # Filter to max_periods
        df = df[df["period_offset"] <= self.max_periods]

        # Count unique users per cohort per offset
        cohort_data = (
            df.groupby(["cohort_period", "period_offset"])[COL_USER_ID]
            .nunique()
            .reset_index(name="users")
        )

        # Pivot into retention table
        retention = cohort_data.pivot(
            index="cohort_period", columns="period_offset", values="users"
        ).fillna(0)

        # Convert to retention rates (divide by period 0 = cohort size)
        cohort_sizes = retention[0]
        retention_rates = retention.div(cohort_sizes, axis=0)

        return retention_rates

    @property
    def table(self) -> pd.DataFrame:
        """Return the retention rate table."""
        return self._retention_table.copy()

    @property
    def average_retention(self) -> pd.Series:
        """Return average retention rate across all cohorts per period."""
        return self._retention_table.mean(axis=0)

    def plot(self, figsize=(14, 8), cmap="YlOrRd", annot=True):
        """
        Plot retention rates as a heatmap.

        Parameters
        ----------
        figsize : tuple
            Figure size.
        cmap : str
            Colormap name.
        annot : bool
            Whether to annotate cells with values.
        """
        fig, ax = plt.subplots(figsize=figsize)

        display_data = self._retention_table.copy()
        display_data.index = display_data.index.astype(str)

        sns.heatmap(
            display_data,
            annot=annot,
            fmt=".0%",
            cmap=cmap,
            vmin=0,
            vmax=1,
            ax=ax,
            linewidths=0.5,
        )

        period_labels = {"D": "Day", "W": "Week", "M": "Month"}
        period_name = period_labels.get(self.period, "Period")

        ax.set_xlabel(f"{period_name} Number")
        ax.set_ylabel("Cohort")
        ax.set_title(f"Retention Analysis ({period_name}ly)")

        plt.tight_layout()
        return fig, ax

    def __repr__(self) -> str:
        n_cohorts = len(self._retention_table)
        return f"RetentionAnalysis(period='{self.period}', cohorts={n_cohorts})"
