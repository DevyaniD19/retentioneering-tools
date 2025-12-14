"""
Retentioneering Tools - User Behavior Analytics Toolkit

A simplified toolkit for analyzing user behavior from event log data.
Supports transition graphs, funnel analysis, retention, cohort analysis,
step matrices, and user clustering.
"""

__version__ = "1.0.0"

from retentioneering.eventstream import EventStream
from retentioneering.preprocessing.data_processor import DataProcessor
from retentioneering.analysis.transition_graph import TransitionGraph
from retentioneering.analysis.funnel import FunnelAnalysis
from retentioneering.analysis.retention import RetentionAnalysis
from retentioneering.analysis.cohort import CohortAnalysis
from retentioneering.analysis.step_matrix import StepMatrix
from retentioneering.analysis.clustering import UserClustering
from retentioneering.visualization.plots import plot_transition_graph, plot_heatmap

__all__ = [
    "EventStream",
    "DataProcessor",
    "TransitionGraph",
    "FunnelAnalysis",
    "RetentionAnalysis",
    "CohortAnalysis",
    "StepMatrix",
    "UserClustering",
    "plot_transition_graph",
    "plot_heatmap",
]
