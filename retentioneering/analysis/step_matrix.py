"""
Step Matrix - Show the distribution of events at each step of the user journey.

Creates a matrix where:
  - Rows = unique events
  - Columns = step number (1st event, 2nd event, ...)
  - Values = fraction of users who had that event at that step
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from retentioneering.constants import COL_USER_ID, COL_EVENT, COL_TIMESTAMP, DEFAULT_MAX_STEPS


class StepMatrix:
    """
    Build a step matrix from an EventStream.

    Parameters
    ----------
    eventstream : EventStream
        The event stream to analyze.
    max_steps : int
        Maximum number of steps to include.
    normalize : bool
        If True, values are fractions (0-1). If False, raw counts.
    """

    def __init__(self, eventstream, max_steps: int = DEFAULT_MAX_STEPS, normalize: bool = True):
        self.eventstream = eventstream
        self.max_steps = max_steps
        self.normalize = normalize
        self._matrix = self._compute_matrix()

    def _compute_matrix(self) -> pd.DataFrame:
        """Compute the step matrix."""
        df = self.eventstream.df.copy()
        df = df.sort_values([COL_USER_ID, COL_TIMESTAMP])

        # Assign step number within each user
        df["step"] = df.groupby(COL_USER_ID).cumcount()

        # Limit to max_steps
        df = df[df["step"] < self.max_steps]

        # Count events at each step
        step_event_counts = (
            df.groupby(["step", COL_EVENT])
            .size()
            .reset_index(name="count")
        )

        # Pivot: rows=events, columns=steps
        matrix = step_event_counts.pivot(
            index=COL_EVENT, columns="step", values="count"
        ).fillna(0)

        if self.normalize:
            # Normalize per step (column): fraction of users at each step
            n_users = df[COL_USER_ID].nunique()
            matrix = matrix / n_users

        # Sort rows by total occurrence (most common events first)
        matrix["_total"] = matrix.sum(axis=1)
        matrix = matrix.sort_values("_total", ascending=False).drop(columns="_total")

        return matrix

    @property
    def matrix(self) -> pd.DataFrame:
        """Return the step matrix."""
        return self._matrix.copy()

    @property
    def top_events(self) -> list:
        """List of events sorted by overall frequency."""
        return list(self._matrix.index)

    def plot(self, max_events: int = 15, figsize=(14, 8), cmap="YlGnBu"):
        """
        Plot the step matrix as a heatmap.

        Parameters
        ----------
        max_events : int
            Maximum number of events (rows) to display.
        figsize : tuple
            Figure size.
        cmap : str
            Colormap.
        """
        fig, ax = plt.subplots(figsize=figsize)

        display_data = self._matrix.head(max_events)

        fmt = ".1%" if self.normalize else ".0f"

        sns.heatmap(
            display_data,
            annot=True,
            fmt=fmt,
            cmap=cmap,
            ax=ax,
            linewidths=0.5,
        )

        ax.set_xlabel("Step Number")
        ax.set_ylabel("Event")
        ax.set_title("Step Matrix")

        plt.tight_layout()
        return fig, ax

    def __repr__(self) -> str:
        rows, cols = self._matrix.shape
        return f"StepMatrix({rows} events x {cols} steps, normalize={self.normalize})"
