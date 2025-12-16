"""
DataProcessor - Preprocessing operations for event streams.

Handles common transformations like:
- Adding session boundaries
- Adding path start/end markers
- Filtering short sessions
- Truncating long paths
- Renaming / grouping events
"""

import pandas as pd
import numpy as np
from retentioneering.constants import (
    COL_USER_ID,
    COL_EVENT,
    COL_TIMESTAMP,
    EVENT_SESSION_START,
    EVENT_SESSION_END,
    EVENT_PATH_START,
    EVENT_PATH_END,
    DEFAULT_SESSION_TIMEOUT_MINUTES,
)


class DataProcessor:
    """
    Preprocessing operations for an EventStream.

    Parameters
    ----------
    eventstream : EventStream
        The event stream to preprocess.
    """

    def __init__(self, eventstream):
        self.eventstream = eventstream

    def add_start_end_events(self):
        """
        Add synthetic path_start before each user's first event
        and path_end after each user's last event.

        Returns
        -------
        EventStream
            A new EventStream with start/end markers added.
        """
        from retentioneering.eventstream import EventStream

        df = self.eventstream.df.copy()

        # Get first and last timestamps per user
        first = df.groupby(COL_USER_ID)[COL_TIMESTAMP].min().reset_index()
        last = df.groupby(COL_USER_ID)[COL_TIMESTAMP].max().reset_index()

        # Create start events (1 second before first event)
        starts = first.copy()
        starts[COL_EVENT] = EVENT_PATH_START
        starts[COL_TIMESTAMP] = starts[COL_TIMESTAMP] - pd.Timedelta(seconds=1)

        # Create end events (1 second after last event)
        ends = last.copy()
        ends[COL_EVENT] = EVENT_PATH_END
        ends[COL_TIMESTAMP] = ends[COL_TIMESTAMP] + pd.Timedelta(seconds=1)

        result = pd.concat([df, starts, ends], ignore_index=True)
        return EventStream(result)

    def split_sessions(self, timeout_minutes: int = DEFAULT_SESSION_TIMEOUT_MINUTES):
        """
        Add session_start and session_end markers based on inactivity gaps.

        A new session starts when the gap between consecutive events
        for a user exceeds timeout_minutes.

        Parameters
        ----------
        timeout_minutes : int
            Inactivity threshold in minutes.

        Returns
        -------
        EventStream
            A new EventStream with session markers added.
        """
        from retentioneering.eventstream import EventStream

        df = self.eventstream.df.copy()
        df = df.sort_values([COL_USER_ID, COL_TIMESTAMP])

        timeout = pd.Timedelta(minutes=timeout_minutes)

        # Compute time gap to previous event per user
        df["prev_time"] = df.groupby(COL_USER_ID)[COL_TIMESTAMP].shift(1)
        df["gap"] = df[COL_TIMESTAMP] - df["prev_time"]

        # Identify session boundaries
        df["new_session"] = (df["gap"] > timeout) | (df["prev_time"].isna())

        new_rows = []
        for _, row in df[df["new_session"]].iterrows():
            # Add session_start just before this event
            new_rows.append(
                {
                    COL_USER_ID: row[COL_USER_ID],
                    COL_EVENT: EVENT_SESSION_START,
                    COL_TIMESTAMP: row[COL_TIMESTAMP] - pd.Timedelta(milliseconds=1),
                }
            )

        # Add session_end after the last event of each session
        df["next_new_session"] = df["new_session"].shift(-1, fill_value=True)
        for _, row in df[df["next_new_session"]].iterrows():
            new_rows.append(
                {
                    COL_USER_ID: row[COL_USER_ID],
                    COL_EVENT: EVENT_SESSION_END,
                    COL_TIMESTAMP: row[COL_TIMESTAMP] + pd.Timedelta(milliseconds=1),
                }
            )

        # Drop helper columns and combine
        df = df.drop(columns=["prev_time", "gap", "new_session", "next_new_session"])

        if new_rows:
            session_df = pd.DataFrame(new_rows)
            result = pd.concat([df, session_df], ignore_index=True)
        else:
            result = df

        return EventStream(result)

    def truncate_paths(self, max_steps: int = 50):
        """
        Keep only the first max_steps events per user.

        Returns
        -------
        EventStream
            A new EventStream with truncated paths.
        """
        from retentioneering.eventstream import EventStream

        df = self.eventstream.df.copy()
        df = df.sort_values([COL_USER_ID, COL_TIMESTAMP])
        df["step"] = df.groupby(COL_USER_ID).cumcount()
        df = df[df["step"] < max_steps].drop(columns=["step"])
        return EventStream(df)

    def rename_events(self, mapping: dict):
        """
        Rename events using a mapping dict.

        Parameters
        ----------
        mapping : dict
            {old_name: new_name} pairs.

        Returns
        -------
        EventStream
            A new EventStream with renamed events.
        """
        from retentioneering.eventstream import EventStream

        df = self.eventstream.df.copy()
        df[COL_EVENT] = df[COL_EVENT].replace(mapping)
        return EventStream(df)

    def group_events(self, groups: dict):
        """
        Group multiple events under a single name.

        Parameters
        ----------
        groups : dict
            {new_name: [list_of_events_to_merge]}.

        Returns
        -------
        EventStream
            A new EventStream with grouped events.
        """
        mapping = {}
        for new_name, old_names in groups.items():
            for old_name in old_names:
                mapping[old_name] = new_name
        return self.rename_events(mapping)

    def filter_short_sessions(self, min_events: int = 2):
        """
        Remove users who have fewer than min_events total events.

        Returns
        -------
        EventStream
            A new EventStream with short sessions removed.
        """
        from retentioneering.eventstream import EventStream

        df = self.eventstream.df.copy()
        user_counts = df.groupby(COL_USER_ID).size()
        valid_users = user_counts[user_counts >= min_events].index
        df = df[df[COL_USER_ID].isin(valid_users)]
        return EventStream(df)
