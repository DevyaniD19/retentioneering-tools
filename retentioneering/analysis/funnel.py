"""
Funnel Analysis - Track user conversion through a sequence of steps.

Given an ordered list of funnel stages (events), computes how many users
reached each stage and the conversion/drop-off rates between stages.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from retentioneering.constants import COL_USER_ID, COL_EVENT, COL_TIMESTAMP


class FunnelAnalysis:
    """
    Analyze user conversion through a defined funnel.

    Parameters
    ----------
    eventstream : EventStream
        The event stream to analyze.
    stages : list of str
        Ordered list of event names defining the funnel steps.
    strict_order : bool
        If True, stages must occur in exact chronological order per user.
        If False, only checks if user performed each event at any time.
    """

    def __init__(self, eventstream, stages: list, strict_order: bool = True):
        self.eventstream = eventstream
        self.stages = stages
        self.strict_order = strict_order
        self._results = self._compute_funnel()

    def _compute_funnel(self) -> pd.DataFrame:
        """Calculate how many users completed each funnel stage."""
        df = self.eventstream.df
        total_users = df[COL_USER_ID].nunique()

        stage_counts = []

        if self.strict_order:
            # For strict order: user must hit stages in sequence
            qualified_users = set(df[COL_USER_ID].unique())

            for i, stage in enumerate(self.stages):
                if i == 0:
                    # Users who performed the first event
                    users_at_stage = set(
                        df[df[COL_EVENT] == stage][COL_USER_ID].unique()
                    )
                else:
                    # Among remaining users, find those who did this event
                    # AFTER their previous stage event
                    prev_stage = self.stages[i - 1]
                    users_at_stage = set()

                    for uid in qualified_users:
                        user_df = df[df[COL_USER_ID] == uid].sort_values(COL_TIMESTAMP)
                        events = user_df[COL_EVENT].tolist()
                        timestamps = user_df[COL_TIMESTAMP].tolist()

                        # Find timestamp of previous stage
                        prev_time = None
                        for ev, ts in zip(events, timestamps):
                            if ev == prev_stage:
                                prev_time = ts
                                break

                        if prev_time is None:
                            continue

                        # Check if current stage happened after previous stage
                        for ev, ts in zip(events, timestamps):
                            if ev == stage and ts >= prev_time:
                                users_at_stage.add(uid)
                                break

                qualified_users = users_at_stage
                stage_counts.append(len(users_at_stage))
        else:
            # Non-strict: just check if user ever did each event
            for stage in self.stages:
                users_with_event = df[df[COL_EVENT] == stage][COL_USER_ID].nunique()
                stage_counts.append(users_with_event)

        results = pd.DataFrame(
            {
                "stage": self.stages,
                "users": stage_counts,
                "conversion_rate": [c / total_users if total_users > 0 else 0 for c in stage_counts],
            }
        )

        # Add step-to-step conversion
        step_conversion = [1.0]
        for i in range(1, len(stage_counts)):
            if stage_counts[i - 1] > 0:
                step_conversion.append(stage_counts[i] / stage_counts[i - 1])
            else:
                step_conversion.append(0.0)
        results["step_conversion"] = step_conversion

        # Add drop-off
        results["drop_off"] = [1.0 - c for c in results["step_conversion"]]

        return results

    @property
    def results(self) -> pd.DataFrame:
        """Return funnel results as a DataFrame."""
        return self._results.copy()

    @property
    def overall_conversion(self) -> float:
        """Conversion rate from first to last stage."""
        if len(self._results) == 0:
            return 0.0
        return self._results["conversion_rate"].iloc[-1]

    def plot(self, figsize=(10, 6), color="#4C72B0"):
        """
        Plot a funnel bar chart showing users at each stage.

        Parameters
        ----------
        figsize : tuple
            Figure size.
        color : str
            Bar color.
        """
        fig, ax = plt.subplots(figsize=figsize)
        results = self._results

        bars = ax.barh(
            range(len(results)),
            results["users"],
            color=color,
            alpha=0.8,
            edgecolor="white",
        )

        ax.set_yticks(range(len(results)))
        ax.set_yticklabels(results["stage"])
        ax.invert_yaxis()
        ax.set_xlabel("Number of Users")
        ax.set_title("Funnel Analysis")

        # Add count and percentage labels
        for i, (count, rate) in enumerate(
            zip(results["users"], results["conversion_rate"])
        ):
            ax.text(
                count + max(results["users"]) * 0.01,
                i,
                f"{count} ({rate:.1%})",
                va="center",
                fontsize=10,
            )

        plt.tight_layout()
        return fig, ax

    def __repr__(self) -> str:
        return (
            f"FunnelAnalysis(stages={self.stages}, "
            f"overall_conversion={self.overall_conversion:.1%})"
        )
