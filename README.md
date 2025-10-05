# Retentioneering Tools

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A simplified Python toolkit for user behavior analytics from event log data.

## Features

- **EventStream** - Load and explore event data from CSV or DataFrame
- **Transition Graph** - Visualize event-to-event transitions as a directed graph
- **Funnel Analysis** - Track user conversion through defined stages
- **Retention Analysis** - Measure how many users return over time periods
- **Cohort Analysis** - Group users by first-activity period and compare behavior
- **Step Matrix** - Show event distribution at each step of the user journey
- **User Clustering** - Cluster users based on behavioral features (KMeans)
- **Preprocessing** - Session splitting, path start/end markers, event grouping

## Installation

```bash
pip install -e .
```

## Quick Start

```python
from retentioneering import EventStream
from retentioneering.sample_data import generate_sample_data

# Generate sample e-commerce data
data = generate_sample_data(n_users=500)
stream = EventStream(data)
print(stream)

# Transition graph
tg = stream.transition_graph(min_weight=10)
tg.plot()

# Funnel analysis
funnel = stream.funnel(stages=["app_open", "catalog", "product_view", "add_to_cart", "purchase_complete"])
funnel.plot()

# Retention
ret = stream.retention(period="W")
ret.plot()

# Cohort analysis
cohort = stream.cohort(period="M", metric="user_count")
cohort.plot()

# Step matrix
sm = stream.step_matrix(max_steps=10)
sm.plot()

# User clustering
clusters = stream.cluster_users(n_clusters=4)
clusters.plot()
```

## Project Structure

```
retentioneering-tools/
├── pyproject.toml
├── README.md
├── retentioneering/
│   ├── __init__.py
│   ├── eventstream.py          # Core EventStream class
│   ├── constants.py            # Default column names & constants
│   ├── utils.py                # Shared utility functions
│   ├── sample_data.py          # Synthetic data generator
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── transition_graph.py # Transition graph builder
│   │   ├── funnel.py           # Funnel analysis
│   │   ├── retention.py        # Retention analysis
│   │   ├── cohort.py           # Cohort analysis
│   │   ├── step_matrix.py      # Step matrix
│   │   └── clustering.py       # User clustering (KMeans)
│   ├── preprocessing/
│   │   ├── __init__.py
│   │   └── data_processor.py   # Data preprocessing operations
│   └── visualization/
│       ├── __init__.py
│       └── plots.py            # Plotting helpers
├── examples/
│   └── quickstart.py           # Full demo script
└── tests/
    ├── __init__.py
    └── test_eventstream.py     # Unit tests
```

## Requirements

- Python >= 3.8
- pandas, numpy, matplotlib, seaborn, networkx, scikit-learn
