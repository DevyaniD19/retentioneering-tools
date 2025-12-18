"""
User Clustering - Cluster users based on behavioral features.

Extracts features from each user's event history and applies
KMeans clustering to group similar users together.
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from retentioneering.constants import COL_USER_ID, COL_EVENT, COL_TIMESTAMP, DEFAULT_N_CLUSTERS


class UserClustering:
    """
    Cluster users based on their behavior patterns.

    Parameters
    ----------
    eventstream : EventStream
        The event stream to analyze.
    n_clusters : int
        Number of clusters.
    features : list of str or None
        Feature extraction methods to use. Options:
        'event_counts', 'session_length', 'event_diversity', 'total_events'.
        If None, uses all available features.
    random_state : int
        Random seed for reproducibility.
    """

    def __init__(
        self,
        eventstream,
        n_clusters: int = DEFAULT_N_CLUSTERS,
        features: list = None,
        random_state: int = 42,
    ):
        self.eventstream = eventstream
        self.n_clusters = n_clusters
        self.feature_names = features or [
            "total_events",
            "unique_events",
            "activity_span_hours",
            "events_per_hour",
        ]
        self.random_state = random_state

        self._feature_matrix = self._extract_features()
        self._labels, self._model = self._run_clustering()

    def _extract_features(self) -> pd.DataFrame:
        """Extract user-level behavioral features."""
        df = self.eventstream.df.copy()

        features = pd.DataFrame()
        features["user_id"] = df[COL_USER_ID].unique()
        features = features.set_index("user_id")

        # Total number of events per user
        features["total_events"] = df.groupby(COL_USER_ID).size()

        # Number of unique event types per user
        features["unique_events"] = df.groupby(COL_USER_ID)[COL_EVENT].nunique()

        # Activity span in hours
        time_range = df.groupby(COL_USER_ID)[COL_TIMESTAMP].agg(["min", "max"])
        span = (time_range["max"] - time_range["min"]).dt.total_seconds() / 3600
        features["activity_span_hours"] = span

        # Events per hour (avoid division by zero)
        features["events_per_hour"] = features["total_events"] / features[
            "activity_span_hours"
        ].replace(0, np.nan).fillna(1)

        # Event type counts as features (top events)
        event_counts = df.groupby([COL_USER_ID, COL_EVENT]).size().unstack(fill_value=0)
        # Keep top 10 most common events to avoid too many features
        top_events = df[COL_EVENT].value_counts().head(10).index
        for event in top_events:
            if event in event_counts.columns:
                features[f"count_{event}"] = event_counts[event]

        features = features.fillna(0)
        return features

    def _run_clustering(self):
        """Run KMeans clustering on extracted features."""
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(self._feature_matrix)

        model = KMeans(
            n_clusters=self.n_clusters,
            random_state=self.random_state,
            n_init=10,
        )
        labels = model.fit_predict(X_scaled)

        return labels, model

    @property
    def feature_matrix(self) -> pd.DataFrame:
        """Return the user feature matrix."""
        return self._feature_matrix.copy()

    @property
    def labels(self) -> np.ndarray:
        """Return cluster labels for each user."""
        return self._labels.copy()

    @property
    def user_clusters(self) -> pd.DataFrame:
        """Return a DataFrame mapping users to their cluster."""
        result = pd.DataFrame(
            {
                "user_id": self._feature_matrix.index,
                "cluster": self._labels,
            }
        )
        return result.reset_index(drop=True)

    @property
    def cluster_sizes(self) -> pd.Series:
        """Return the number of users in each cluster."""
        return pd.Series(self._labels).value_counts().sort_index()

    def cluster_profiles(self) -> pd.DataFrame:
        """
        Return the mean feature values per cluster.
        Useful for understanding what defines each cluster.
        """
        fm = self._feature_matrix.copy()
        fm["cluster"] = self._labels
        return fm.groupby("cluster").mean()

    def plot(self, figsize=(10, 6)):
        """
        Plot cluster sizes and average feature profiles.

        Parameters
        ----------
        figsize : tuple
            Figure size.
        """
        fig, axes = plt.subplots(1, 2, figsize=figsize)

        # Cluster sizes
        sizes = self.cluster_sizes
        axes[0].bar(sizes.index, sizes.values, color="#4C72B0", alpha=0.8)
        axes[0].set_xlabel("Cluster")
        axes[0].set_ylabel("Number of Users")
        axes[0].set_title("Cluster Sizes")
        axes[0].set_xticks(sizes.index)

        # Feature profiles (normalized for comparison)
        profiles = self.cluster_profiles()
        # Normalize each feature to 0-1 for visual comparison
        norm_profiles = (profiles - profiles.min()) / (
            profiles.max() - profiles.min() + 1e-10
        )
        # Only show first few features for readability
        display_cols = norm_profiles.columns[:6]
        norm_profiles[display_cols].T.plot(
            kind="bar", ax=axes[1], alpha=0.8, width=0.8
        )
        axes[1].set_title("Cluster Feature Profiles (normalized)")
        axes[1].set_xlabel("Feature")
        axes[1].set_ylabel("Normalized Value")
        axes[1].legend(title="Cluster", bbox_to_anchor=(1.05, 1))
        axes[1].tick_params(axis="x", rotation=45)

        plt.tight_layout()
        return fig, axes

    def __repr__(self) -> str:
        n_users = len(self._feature_matrix)
        return (
            f"UserClustering(n_clusters={self.n_clusters}, "
            f"users={n_users}, features={len(self._feature_matrix.columns)})"
        )
