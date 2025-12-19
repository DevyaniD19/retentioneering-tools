"""
Visualization Helpers - Reusable plotting functions for the toolkit.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
import numpy as np
import pandas as pd


def plot_transition_graph(
    graph: nx.DiGraph,
    figsize=(12, 8),
    node_size=2000,
    font_size=9,
    edge_label_font_size=8,
    node_color="#66b3ff",
    edge_color="#888888",
    layout="spring",
    title="Transition Graph",
):
    """
    Draw a directed transition graph using matplotlib and networkx.

    Parameters
    ----------
    graph : nx.DiGraph
        A networkx directed graph with 'weight' edge attributes.
    figsize : tuple
        Figure size.
    node_size : int
        Size of nodes.
    font_size : int
        Font size for node labels.
    edge_label_font_size : int
        Font size for edge weight labels.
    node_color : str
        Color of nodes.
    edge_color : str
        Color of edges.
    layout : str
        Layout algorithm: 'spring', 'circular', 'shell', 'kamada_kawai'.
    title : str
        Plot title.

    Returns
    -------
    fig, ax
    """
    fig, ax = plt.subplots(figsize=figsize)

    # Choose layout
    layout_funcs = {
        "spring": nx.spring_layout,
        "circular": nx.circular_layout,
        "shell": nx.shell_layout,
        "kamada_kawai": nx.kamada_kawai_layout,
    }
    layout_func = layout_funcs.get(layout, nx.spring_layout)
    pos = layout_func(graph, seed=42)

    # Get edge weights for width scaling
    weights = [graph[u][v]["weight"] for u, v in graph.edges()]
    if weights:
        max_w = max(weights)
        min_w = min(weights)
        if max_w > min_w:
            scaled_widths = [1 + 4 * (w - min_w) / (max_w - min_w) for w in weights]
        else:
            scaled_widths = [2] * len(weights)
    else:
        scaled_widths = []

    # Draw nodes
    nx.draw_networkx_nodes(
        graph, pos, node_size=node_size, node_color=node_color,
        alpha=0.9, edgecolors="white", linewidths=2, ax=ax,
    )

    # Draw edges
    nx.draw_networkx_edges(
        graph, pos, width=scaled_widths, edge_color=edge_color,
        alpha=0.6, arrows=True, arrowsize=20,
        connectionstyle="arc3,rad=0.1", ax=ax,
    )

    # Draw labels
    nx.draw_networkx_labels(
        graph, pos, font_size=font_size, font_weight="bold", ax=ax,
    )

    # Edge labels (weights)
    edge_labels = {(u, v): f"{d['weight']:.2g}" for u, v, d in graph.edges(data=True)}
    nx.draw_networkx_edge_labels(
        graph, pos, edge_labels=edge_labels,
        font_size=edge_label_font_size, ax=ax,
    )

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.axis("off")
    plt.tight_layout()
    return fig, ax


def plot_heatmap(
    data: pd.DataFrame,
    figsize=(12, 8),
    cmap="YlOrRd",
    annot=True,
    fmt=".2f",
    title="Heatmap",
    xlabel="",
    ylabel="",
):
    """
    Generic heatmap plotting function.

    Parameters
    ----------
    data : pd.DataFrame
        2D data to plot.
    figsize : tuple
        Figure size.
    cmap : str
        Colormap name.
    annot : bool
        Annotate cells with values.
    fmt : str
        Format string for annotations.
    title : str
        Plot title.
    xlabel, ylabel : str
        Axis labels.

    Returns
    -------
    fig, ax
    """
    fig, ax = plt.subplots(figsize=figsize)

    sns.heatmap(
        data,
        annot=annot,
        fmt=fmt,
        cmap=cmap,
        ax=ax,
        linewidths=0.5,
    )

    ax.set_title(title, fontsize=14, fontweight="bold")
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)

    plt.tight_layout()
    return fig, ax


def plot_event_frequency(event_counts: pd.Series, top_n: int = 20, figsize=(10, 6)):
    """
    Plot a horizontal bar chart of event frequencies.

    Parameters
    ----------
    event_counts : pd.Series
        Event name -> count, sorted descending.
    top_n : int
        Number of top events to show.
    figsize : tuple
        Figure size.

    Returns
    -------
    fig, ax
    """
    fig, ax = plt.subplots(figsize=figsize)

    data = event_counts.head(top_n)
    colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(data)))

    ax.barh(range(len(data)), data.values, color=colors, alpha=0.85)
    ax.set_yticks(range(len(data)))
    ax.set_yticklabels(data.index)
    ax.invert_yaxis()
    ax.set_xlabel("Count")
    ax.set_title("Event Frequency (Top {})".format(top_n))

    plt.tight_layout()
    return fig, ax
