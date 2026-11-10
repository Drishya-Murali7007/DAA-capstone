# Project Report: Intelligent Courier Planning System

## 1. Problem definition

A courier has a fixed-capacity vehicle, a set of parcels, a depot, and a road network.
The system must decide which parcels fit in the vehicle, prioritize them for processing,
and determine a practical delivery sequence that minimizes travel distance approximately.

## 2. Data model

Each parcel has an ID, destination node, weight, value score, priority, and deadline rank.
The road network is a weighted undirected graph represented by an adjacency list.
An edge weight represents distance in kilometres.

## 3. Integrated workflow

```text
Parcel CSV ──> Merge Sort by priority/deadline ──> Ordered parcels
                                                    │
                                                    v
                                             0/1 Knapsack DP
                                                    │
                                     Selected parcels + packed weight
                                                    │
                                                    v
Road edge list ──> Adjacency-list graph ──> Dijkstra shortest paths
                                                    │
                                                    v
                                      Nearest-neighbor TSP heuristic
                                                    │
                                                    v
                                   Delivery order + route distance
                                                    │
                                                    v
                                     Runtime benchmark + report
```

## 4. Algorithm choices

### 4.1 Merge Sort

The parcel list is sorted by descending priority, ascending deadline, and ID as a
deterministic tie-breaker. Merge Sort guarantees `O(n log n)` time and is stable.

### 4.2 0/1 Knapsack using dynamic programming

For parcel `i` and capacity `c`, the recurrence is:

`DP[i][c] = max(DP[i-1][c], value[i] + DP[i-1][c-weight[i]])`

when the parcel fits; otherwise `DP[i][c] = DP[i-1][c]`.
The final DP cell gives the maximum total value for the selected capacity. Backtracking
recovers the parcel IDs. The implementation scales weights to integer tenths of a kg.

### 4.3 Dijkstra's algorithm

The graph is stored as an adjacency list. A min-heap selects the currently closest
unprocessed vertex. The algorithm returns shortest distances and predecessor links,
which are used to reconstruct road paths.

### 4.4 Nearest-neighbor TSP approximation

Starting at `DEPOT`, choose the unvisited delivery point with the smallest Dijkstra
distance from the current point. Repeat until all selected destinations are visited,
then return to the depot. This is a practical heuristic; it does not guarantee the
globally shortest travelling-salesperson tour.

## 5. Sample execution and evidence

Run `python courier_planner.py` to display:
- priority-sorted parcels;
- selected parcel IDs, packed weight, and total value;
- a sample of the final DP row;
- delivery stop order and expanded road path;
- total route distance, including the return to the depot;
- mean runtime of the major algorithm components.

The `screenshots/` folder contains a terminal-style sample output image.
The `charts/` folder contains a runtime comparison chart generated from repeated runs.

## 6. Performance testing

The benchmark measures each major component independently using `time.perf_counter()`.
Each measurement is the mean of five runs. Small sample inputs are useful for correctness
demonstrations, but their runtimes are dominated by interpreter and timer overhead.
For meaningful scalability analysis, increase the parcel and graph sizes and repeat the
benchmark. Compare growth trends rather than treating one tiny timing as a universal result.

## 7. Correctness checks

Unit tests validate:
- parcel sorting order;
- knapsack capacity and optimal value on a small known case;
- Dijkstra shortest distance and reconstructed path;
- route closure at the depot and positive total distance.

## 8. Future improvements

- Add time-window feasibility and deadline penalties.
- Include parcel volume and 3D box dimensions in packing.
- Support directed roads and live traffic weights.
- Use 2-opt or simulated annealing to improve the nearest-neighbor tour.
- Use multi-vehicle capacitated vehicle-routing heuristics.
- Add a GUI, map visualization, and persistent delivery manifests.
- Benchmark multiple sorting methods and compare Dijkstra with Bellman-Ford/Floyd-Warshall
  on datasets where their assumptions and graph sizes make the comparison meaningful.

## 9. Conclusion

The prototype demonstrates an end-to-end algorithmic courier workflow. Sorting handles
parcel urgency, dynamic programming optimizes the load's total value, Dijkstra supplies
shortest road distances, and nearest-neighbor constructs a feasible approximate tour.
Runtime measurements make the computational cost of each stage observable.

## 10. Larger-dataset experiment

`benchmark_scaling.py` generates deterministic synthetic datasets at 20, 80 and 200 parcels, scales the road graph with the dataset, and measures Merge Sort, Knapsack DP, Dijkstra and a bounded nearest-neighbor route. The output chart is `charts/runtime_scaling.png`. The benchmark is intended to compare growth trends; absolute values vary by machine and Python version.
