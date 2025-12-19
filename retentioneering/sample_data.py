"""
Sample Data Generator - Create realistic synthetic event log data for testing.
"""

import pandas as pd
import numpy as np
from retentioneering.constants import COL_USER_ID, COL_EVENT, COL_TIMESTAMP


def generate_sample_data(
    n_users: int = 500,
    start_date: str = "2025-01-01",
    days: int = 90,
    random_seed: int = 42,
) -> pd.DataFrame:
    """
    Generate synthetic user event data simulating an e-commerce app.

    Parameters
    ----------
    n_users : int
        Number of unique users.
    start_date : str
        Start date for the data.
    days : int
        Number of days of data to generate.
    random_seed : int
        Random seed for reproducibility.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns [user_id, event, timestamp].
    """
    rng = np.random.RandomState(random_seed)

    # Define events with transition probabilities
    events = [
        "app_open",
        "main_page",
        "catalog",
        "product_view",
        "add_to_cart",
        "cart_view",
        "checkout",
        "payment",
        "purchase_complete",
        "search",
        "filter_apply",
        "review_view",
        "profile",
        "settings",
        "logout",
    ]

    # Transition probability matrix (simplified - from each event, where they go next)
    # Higher probability paths represent realistic user flows
    transitions = {
        "app_open": {"main_page": 0.8, "search": 0.15, "profile": 0.05},
        "main_page": {"catalog": 0.4, "search": 0.25, "profile": 0.1, "logout": 0.05, "settings": 0.05, "product_view": 0.15},
        "catalog": {"product_view": 0.5, "filter_apply": 0.2, "search": 0.15, "main_page": 0.1, "logout": 0.05},
        "product_view": {"add_to_cart": 0.3, "review_view": 0.15, "catalog": 0.25, "search": 0.1, "main_page": 0.15, "logout": 0.05},
        "add_to_cart": {"cart_view": 0.5, "catalog": 0.25, "product_view": 0.15, "checkout": 0.1},
        "cart_view": {"checkout": 0.4, "catalog": 0.3, "product_view": 0.15, "main_page": 0.1, "logout": 0.05},
        "checkout": {"payment": 0.6, "cart_view": 0.25, "main_page": 0.1, "logout": 0.05},
        "payment": {"purchase_complete": 0.8, "checkout": 0.1, "main_page": 0.05, "logout": 0.05},
        "purchase_complete": {"main_page": 0.4, "catalog": 0.3, "logout": 0.3},
        "search": {"catalog": 0.4, "product_view": 0.35, "main_page": 0.15, "logout": 0.1},
        "filter_apply": {"product_view": 0.5, "catalog": 0.3, "search": 0.1, "main_page": 0.1},
        "review_view": {"product_view": 0.4, "add_to_cart": 0.25, "catalog": 0.2, "main_page": 0.1, "logout": 0.05},
        "profile": {"settings": 0.3, "main_page": 0.4, "catalog": 0.2, "logout": 0.1},
        "settings": {"main_page": 0.5, "profile": 0.3, "logout": 0.2},
        "logout": {},
    }

    base_date = pd.Timestamp(start_date)
    records = []

    for user_id in range(1, n_users + 1):
        # Each user has 1-5 sessions over the time period
        n_sessions = rng.randint(1, 6)

        for session in range(n_sessions):
            # Random session start time
            session_day = rng.randint(0, days)
            session_hour = rng.randint(6, 23)
            session_minute = rng.randint(0, 60)
            session_start = base_date + pd.Timedelta(
                days=session_day, hours=session_hour, minutes=session_minute
            )

            # Generate event sequence for this session
            current_event = "app_open"
            current_time = session_start

            # Each session has 3-25 events
            max_events = rng.randint(3, 26)

            for step in range(max_events):
                records.append(
                    {
                        COL_USER_ID: f"user_{user_id:04d}",
                        COL_EVENT: current_event,
                        COL_TIMESTAMP: current_time,
                    }
                )

                if current_event == "logout" or current_event not in transitions:
                    break

                # Pick next event based on transition probabilities
                trans = transitions[current_event]
                if not trans:
                    break

                next_events = list(trans.keys())
                probs = list(trans.values())
                current_event = rng.choice(next_events, p=probs)

                # Random time between events (5 seconds to 5 minutes)
                gap_seconds = rng.randint(5, 300)
                current_time = current_time + pd.Timedelta(seconds=gap_seconds)

    df = pd.DataFrame(records)
    df = df.sort_values(COL_TIMESTAMP).reset_index(drop=True)
    return df
