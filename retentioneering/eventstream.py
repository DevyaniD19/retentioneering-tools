"""
EventStream - Core class for loading and working with user event data.

This is the main entry point for the toolkit. It wraps a pandas DataFrame
of events and provides convenient access to all analysis tools.
"""

import pandas as pd
from retentioneering.constants import COL_USER_ID, COL_EVENT, COL_TIMESTAMP
from retentioneering.utils import validate_dataframe, sort_events, to_datetime
from retentioneering.utils import event_frequency, count_unique_users, get_user_paths


class EventStream:
    """
    Core class that holds user event data and provides analysis methods.

    Parameters
    ----------
    data : pd.DataFrame or str
        Either a DataFrame with columns [user_id, event, timestamp],
        or a file path to a CSV file.
    user_col : str
        Name of the user ID column (renamed to 'user_id' internally).
    event_col : str
        Name of the event column (renamed to 'event' internally).
    timestamp_col : str
        Name of the timestamp column (renamed to 'timestamp' internally).
    """

    def __init__(
        self,
        data,
        user_col: str = "user_id",
        event_col: str = "event",
        timestamp_col: str = "timestamp",
    ):
        if isinstance(data, str):
            df = pd.read_csv(data)
        elif isinstance(data, pd.DataFrame):
            df = data.copy()
        else:
            raise TypeError("data must be a DataFrame or a CSV file path")

        # Rename columns to standard names
        rename_map = {}
        if user_col != COL_USER_ID:
            rename_map[user_col] = COL_USER_ID
        if event_col != COL_EVENT:
            rename_map[event_col] = COL_EVENT
        if timestamp_col != COL_TIMESTAMP:
            rename_map[timestamp_col] = COL_TIMESTAMP
        if rename_map:
            df = df.rename(columns=rename_map)

        validate_dataframe(df)
        df = to_datetime(df)
        self.df = sort_events(df)

    def __repr__(self) -> str:
        n_users = self.user_count
        n_events = len(self.df)
        n_types = self.df[COL_EVENT].nunique()
        return (
            f"EventStream({n_events} events, {n_users} users, {n_types} event types)"
        )

    @property
    def user_count(self) -> int:
        """Number of unique users."""
        return count_unique_users(self.df)

    @property
    def events(self) -> pd.Series:
        """Event frequency counts."""
        return event_frequency(self.df)

    @property
    def user_paths(self) -> dict:
        """Dict of user_id -> list of events in order."""
        return get_user_paths(self.df)

    def head(self, n: int = 10) -> pd.DataFrame:
        """Return first n rows."""
        return self.df.head(n)

    def filter_events(self, events: list) -> "EventStream":
        """Return a new EventStream containing only the specified events."""
        filtered = self.df[self.df[COL_EVENT].isin(events)]
        return EventStream(filtered)

    def filter_users(self, user_ids: list) -> "EventStream":
        """Return a new EventStream containing only the specified users."""
        filtered = self.df[self.df[COL_USER_ID].isin(user_ids)]
        return EventStream(filtered)

    def date_range(self, start=None, end=None) -> "EventStream":
        """Filter events by date range."""
        df = self.df.copy()
        if start:
            df = df[df[COL_TIMESTAMP] >= pd.to_datetime(start)]
        if end:
            df = df[df[COL_TIMESTAMP] <= pd.to_datetime(end)]
        return EventStream(df)

    def add_start_end_events(self) -> "EventStream":
        """Add synthetic path_start and path_end events per user."""
        from retentioneering.preprocessing.data_processor import DataProcessor
        processor = DataProcessor(self)
        return processor.add_start_end_events()

    def split_sessions(self, timeout_minutes: int = 30) -> "EventStream":
        """Add session_start / session_end markers based on inactivity gap."""
        from retentioneering.preprocessing.data_processor import DataProcessor
        processor = DataProcessor(self)
        return processor.split_sessions(timeout_minutes)

    def transition_graph(self, **kwargs):
        """Build a transition graph from this event stream."""
        from retentioneering.analysis.transition_graph import TransitionGraph
        return TransitionGraph(self, **kwargs)

    def funnel(self, stages: list, **kwargs):
        """Run funnel analysis on this event stream."""
        from retentioneering.analysis.funnel import FunnelAnalysis
        return FunnelAnalysis(self, stages=stages, **kwargs)

    def retention(self, **kwargs):
        """Run retention analysis on this event stream."""
        from retentioneering.analysis.retention import RetentionAnalysis
        return RetentionAnalysis(self, **kwargs)

    def cohort(self, **kwargs):
        """Run cohort analysis on this event stream."""
        from retentioneering.analysis.cohort import CohortAnalysis
        return CohortAnalysis(self, **kwargs)

    def step_matrix(self, **kwargs):
        """Build a step matrix from this event stream."""
        from retentioneering.analysis.step_matrix import StepMatrix
        return StepMatrix(self, **kwargs)

    def cluster_users(self, **kwargs):
        """Cluster users based on their event sequences."""
        from retentioneering.analysis.clustering import UserClustering
        return UserClustering(self, **kwargs)
