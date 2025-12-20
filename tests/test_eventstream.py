"""Tests for EventStream and analysis modules."""

import pytest
import pandas as pd
import numpy as np


def make_sample_df():
    """Create a small test dataset."""
    return pd.DataFrame(
        {
            "user_id": ["u1", "u1", "u1", "u2", "u2", "u2", "u3", "u3"],
            "event": [
                "home", "search", "purchase",
                "home", "search", "logout",
                "home", "purchase",
            ],
            "timestamp": pd.to_datetime([
                "2025-01-01 10:00", "2025-01-01 10:05", "2025-01-01 10:10",
                "2025-01-01 11:00", "2025-01-01 11:05", "2025-01-01 11:10",
                "2025-01-02 09:00", "2025-01-02 09:15",
            ]),
        }
    )


def test_eventstream_creation():
    from retentioneering.eventstream import EventStream
    df = make_sample_df()
    stream = EventStream(df)
    assert stream.user_count == 3
    assert len(stream.df) == 8


def test_eventstream_filter_events():
    from retentioneering.eventstream import EventStream
    df = make_sample_df()
    stream = EventStream(df)
    filtered = stream.filter_events(["home", "purchase"])
    assert set(filtered.df["event"].unique()) == {"home", "purchase"}


def test_eventstream_filter_users():
    from retentioneering.eventstream import EventStream
    df = make_sample_df()
    stream = EventStream(df)
    filtered = stream.filter_users(["u1", "u3"])
    assert set(filtered.df["user_id"].unique()) == {"u1", "u3"}


def test_transition_graph():
    from retentioneering.eventstream import EventStream
    df = make_sample_df()
    stream = EventStream(df)
    tg = stream.transition_graph()
    assert len(tg.nodes) > 0
    assert len(tg.edges) > 0


def test_funnel():
    from retentioneering.eventstream import EventStream
    df = make_sample_df()
    stream = EventStream(df)
    funnel = stream.funnel(stages=["home", "search", "purchase"])
    assert len(funnel.results) == 3
    assert funnel.results.iloc[0]["users"] == 3  # all users hit "home"


def test_step_matrix():
    from retentioneering.eventstream import EventStream
    df = make_sample_df()
    stream = EventStream(df)
    sm = stream.step_matrix(max_steps=5)
    assert sm.matrix.shape[1] <= 5


def test_clustering():
    from retentioneering.eventstream import EventStream
    df = make_sample_df()
    stream = EventStream(df)
    cl = stream.cluster_users(n_clusters=2)
    assert len(cl.user_clusters) == 3
    assert cl.cluster_sizes.sum() == 3


def test_add_start_end():
    from retentioneering.eventstream import EventStream
    df = make_sample_df()
    stream = EventStream(df)
    processed = stream.add_start_end_events()
    events = processed.df["event"].unique()
    assert "path_start" in events
    assert "path_end" in events


def test_sample_data():
    from retentioneering.sample_data import generate_sample_data
    df = generate_sample_data(n_users=10, days=7)
    assert len(df) > 0
    assert "user_id" in df.columns
    assert "event" in df.columns
    assert "timestamp" in df.columns


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
