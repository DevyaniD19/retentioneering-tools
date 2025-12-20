"""
Quickstart Example - Demonstrates all major features of the toolkit.

Run this script to see the toolkit in action with synthetic data.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from retentioneering import EventStream
from retentioneering.sample_data import generate_sample_data
from retentioneering.visualization.plots import plot_event_frequency


def main():
    # ----------------------------------------------------------------
    # 1. Generate sample data and create an EventStream
    # ----------------------------------------------------------------
    print("=== Generating sample data ===")
    data = generate_sample_data(n_users=200, days=60)
    stream = EventStream(data)
    print(stream)
    print(f"\nFirst 5 rows:\n{stream.head(5)}")
    print(f"\nEvent frequencies:\n{stream.events.head(10)}")

    # ----------------------------------------------------------------
    # 2. Preprocessing - add start/end markers
    # ----------------------------------------------------------------
    print("\n=== Preprocessing ===")
    processed = stream.add_start_end_events()
    print(f"After adding start/end events: {processed}")

    # ----------------------------------------------------------------
    # 3. Transition Graph
    # ----------------------------------------------------------------
    print("\n=== Transition Graph ===")
    tg = stream.transition_graph(min_weight=10)
    print(tg)
    print(f"\nTop 10 transitions:\n{tg.top_transitions(10)}")

    # Uncomment to plot:
    # tg.plot(layout="kamada_kawai")
    # import matplotlib.pyplot as plt
    # plt.show()

    # ----------------------------------------------------------------
    # 4. Funnel Analysis
    # ----------------------------------------------------------------
    print("\n=== Funnel Analysis ===")
    funnel = stream.funnel(
        stages=["app_open", "catalog", "product_view", "add_to_cart", "checkout", "payment", "purchase_complete"]
    )
    print(funnel)
    print(f"\nFunnel results:\n{funnel.results}")

    # Uncomment to plot:
    # funnel.plot()
    # import matplotlib.pyplot as plt
    # plt.show()

    # ----------------------------------------------------------------
    # 5. Retention Analysis
    # ----------------------------------------------------------------
    print("\n=== Retention Analysis ===")
    ret = stream.retention(period="W", max_periods=8)
    print(ret)
    print(f"\nAverage retention by week:\n{ret.average_retention}")

    # Uncomment to plot:
    # ret.plot()
    # import matplotlib.pyplot as plt
    # plt.show()

    # ----------------------------------------------------------------
    # 6. Cohort Analysis
    # ----------------------------------------------------------------
    print("\n=== Cohort Analysis ===")
    cohort = stream.cohort(period="W", metric="user_count")
    print(cohort)
    print(f"\nCohort sizes:\n{cohort.cohort_sizes}")

    # Uncomment to plot:
    # cohort.plot()
    # import matplotlib.pyplot as plt
    # plt.show()

    # ----------------------------------------------------------------
    # 7. Step Matrix
    # ----------------------------------------------------------------
    print("\n=== Step Matrix ===")
    sm = stream.step_matrix(max_steps=10)
    print(sm)
    print(f"\nStep matrix (first 5 events, first 5 steps):\n{sm.matrix.iloc[:5, :5]}")

    # Uncomment to plot:
    # sm.plot(max_events=10)
    # import matplotlib.pyplot as plt
    # plt.show()

    # ----------------------------------------------------------------
    # 8. User Clustering
    # ----------------------------------------------------------------
    print("\n=== User Clustering ===")
    clusters = stream.cluster_users(n_clusters=4)
    print(clusters)
    print(f"\nCluster sizes:\n{clusters.cluster_sizes}")
    print(f"\nCluster profiles:\n{clusters.cluster_profiles().round(2)}")

    # Uncomment to plot:
    # clusters.plot()
    # import matplotlib.pyplot as plt
    # plt.show()

    print("\n=== Done! Uncomment plot lines and add plt.show() to see visualizations ===")


if __name__ == "__main__":
    main()
