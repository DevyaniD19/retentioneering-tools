"""
Cohort Analysis - Group users by their first-activity period and compare behavior.

Tracks metrics (event counts, unique events, session counts) per cohort over time.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from retentioneering.constants import COL_USER_ID, COL_EVENT, COL_TIMESTAMP


class CohortAnalysis:
    """
    Group users into cohorts by their first activity period and analyze behavior.

    Parameters
    ----------
    eventstream : EventStream
        The event stream to analyze.
    period : str
        Time period for cohort grouping: 'D', 'W', 'M'.
    metric : str
        Metric to compute: 'event_count', 'unique_events', 'user_count'.
    """

    def __init__(self, eventstream, period: str = "M", metric: str = "event_count"):
        self.eventstream = eventstream
        self.period = period
        self.metric = metric
        self._cohort_table = self._compute_cohorts()

    def _compute_cohorts(self) -> pd.DataFrame:
        """Compute cohort metrics."""
        df = self.eventstream.df.copy()

        # Assign periods
        df["activity_period"] = df[COL_TIMESTAMP].dt.to_period(self.period)

        # Find cohort (first activity period) per user
        cohort_map = (
            df.groupby(COL_USER_ID)["activity_period"]
            .min()
            .reset_index()
            .rename(columns={"activity_period": "cohort"})
        )
        df = df.merge(cohort_map, on=COL_USER_ID)

        # Compute period offset
        df["period_offset"] = (
            df["activity_period"].apply(lambda x: x.ordinal)
            - df["cohort"].apply(lambda x: x.ordinal)
        )

        # Compute the chosen metric per cohort per offset
        if self.metric == "event_count":
            result = (
                df.groupby(["cohort", "period_offset"])
                .size()
                .reset_index(name="value")
            )
        elif self.metric == "unique_events":
            result = (
                df.groupby(["cohort", "period_offset"])[COL_EVENT]
                .nunique()
                .reset_index(name="value")
            )
        elif self.metric == "user_count":
            result = (
                df.groupby(["cohort", "period_offset"])[COL_USER_ID]
                .nunique()
                .reset_index(name="value")
            )
        else:
            raise ValueError(
                f"Unknown metric '{self.metric}'. "
                "Choose from: event_count, unique_events, user_count"
            )

        # Pivot
        table = result.pivot(
            index="cohort", columns="period_offset", values="value"
        ).fillna(0)

        return table

    @property
    def table(self) -> pd.DataFrame:
        """Return the cohort table."""
        return self._cohort_table.copy()

    @property
    def cohort_sizes(self) -> pd.Series:
        """Return the size (user count) of each cohort."""
        df = self.eventstream.df.copy()
        df["cohort"] = df.groupby(COL_USER_ID)[COL_TIMESTAMP].transform("min").dt.to_period(self.period)
        return df.groupby("cohort")[COL_USER_ID].nunique()

    def plot(self, figsize=(14, 8), cmap="Blues", annot=True):
        """Plot the cohort table as a heatmap."""
        fig, ax = plt.subplots(figsize=figsize)

        display_data = self._cohort_table.copy()
        display_data.index = display_data.index.astype(str)

        sns.heatmap(
            display_data,
            annot=annot,
            fmt=".0f",
            cmap=cmap,
            ax=ax,
            linewidths=0.5,
        )

        period_labels = {"D": "Day", "W": "Week", "M": "Month"}
        period_name = period_labels.get(self.period, "Period")

        ax.set_xlabel(f"{period_name} Offset")
        ax.set_ylabel("Cohort")
        ax.set_title(f"Cohort Analysis - {self.metric} ({period_name}ly)")

        plt.tight_layout()
        return fig, ax

    def __repr__(self) -> str:
        n = len(self._cohort_table)
        return f"CohortAnalysis(period='{self.period}', metric='{self.metric}', cohorts={n})"
