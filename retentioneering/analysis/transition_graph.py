"""
Transition Graph - Visualize event-to-event transitions as a directed graph.

Builds a weighted directed graph where:
  - Nodes = unique events
  - Edges = transitions between consecutive events (per user)
  - Edge weight = number of times that transition occurred
"""

import pandas as pd
import numpy as np
import networkx as nx
from retentioneering.constants import COL_USER_ID, COL_EVENT, COL_TIMESTAMP


class TransitionGraph:
    """
    Build and analyze a transition graph from an EventStream.

    Parameters
    ----------
    eventstream : EventStream
        The event stream to analyze.
    norm : bool
        If True, normalize edge weights to transition probabilities (0-1).
    min_weight : int
        Minimum edge weight to include (filters out rare transitions).
    """

    def __init__(self, eventstream, norm: bool = False, min_weight: int = 0):
        self.eventstream = eventstream
        self.norm = norm
        self.min_weight = min_weight

        self._edges = self._compute_edges()
        self.graph = self._build_graph()

    def _compute_edges(self) -> pd.DataFrame:
        """Compute transition counts between consecutive events per user."""
        df = self.eventstream.df.copy()
        df = df.sort_values([COL_USER_ID, COL_TIMESTAMP])

        # Create next-event column (within same user)
        df["next_event"] = df.groupby(COL_USER_ID)[COL_EVENT].shift(-1)
        transitions = df.dropna(subset=["next_event"])

        # Count transitions
        edge_counts = (
            transitions.groupby([COL_EVENT, "next_event"])
            .size()
            .reset_index(name="weight")
        )
        edge_counts.columns = ["source", "target", "weight"]

        if self.min_weight > 0:
            edge_counts = edge_counts[edge_counts["weight"] >= self.min_weight]

        if self.norm:
            # Normalize: each source's outgoing edges sum to 1
            totals = edge_counts.groupby("source")["weight"].transform("sum")
            edge_counts["weight"] = edge_counts["weight"] / totals

        return edge_counts.reset_index(drop=True)

    def _build_graph(self) -> nx.DiGraph:
        """Build a networkx directed graph from computed edges."""
        G = nx.DiGraph()
        for _, row in self._edges.iterrows():
            G.add_edge(row["source"], row["target"], weight=row["weight"])
        return G

    @property
    def edges(self) -> pd.DataFrame:
        """Return the edge list as a DataFrame."""
        return self._edges.copy()

    @property
    def nodes(self) -> list:
        """Return the list of unique events (nodes)."""
        return list(self.graph.nodes)

    @property
    def adjacency_matrix(self) -> pd.DataFrame:
        """Return the adjacency matrix as a DataFrame."""
        nodes = sorted(self.graph.nodes)
        matrix = nx.to_pandas_adjacency(self.graph, nodelist=nodes, weight="weight")
        return matrix

    def top_transitions(self, n: int = 10) -> pd.DataFrame:
        """Return the top n transitions by weight."""
        return self._edges.sort_values("weight", ascending=False).head(n)

    def plot(self, figsize=(12, 8), node_size=2000, font_size=9, **kwargs):
        """
        Draw the transition graph using matplotlib.

        Parameters
        ----------
        figsize : tuple
            Figure size.
        node_size : int
            Size of nodes.
        font_size : int
            Font size for labels.
        """
        from retentioneering.visualization.plots import plot_transition_graph
        return plot_transition_graph(
            self.graph,
            figsize=figsize,
            node_size=node_size,
            font_size=font_size,
            **kwargs,
        )

    def __repr__(self) -> str:
        return (
            f"TransitionGraph({len(self.nodes)} nodes, "
            f"{len(self._edges)} edges, norm={self.norm})"
        )
