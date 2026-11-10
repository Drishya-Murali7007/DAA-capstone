# Intelligent Courier Planner

A Python prototype that combines sorting, dynamic programming, graph algorithms,
a TSP approximation, and runtime benchmarking into one courier-planning workflow.

## Features

1. **Parcel prioritization — Merge Sort**  
   Stable ordering by priority (descending), then deadline (ascending), then parcel ID.
2. **Packing optimization — 0/1 Knapsack DP**  
   Maximizes the total parcel value without exceeding the vehicle's weight capacity.
   Parcel weights are represented in tenths of a kilogram.
3. **Shortest paths — Dijkstra**  
   Computes shortest road distances from a source node using an adjacency list and a min-heap.
4. **Delivery sequence — Nearest-neighbor TSP approximation**  
   Repeatedly visits the unvisited delivery point with the smallest shortest-path distance,
   then returns to the depot. The route is a heuristic, not a guaranteed optimal TSP tour.
5. **Performance analysis**  
   Measures mean runtime for the major algorithmic components over repeated runs.

## Project structure

```text
courier_planner_project/
├── courier_planner.py
├── README.md
├── REPORT.md
├── requirements.txt
├── data/
│   ├── parcels.csv
│   └── roads.csv
├── tests/
│   └── test_courier_planner.py
├── charts/
│   └── runtime_comparison.png
└── screenshots/
    └── sample_output.png
```

## Requirements

- Python 3.9 or newer
- No third-party packages are needed to run the planner.
- Matplotlib is only needed to regenerate the runtime chart: `pip install matplotlib`.

## Run

Open a terminal in this folder:

```bash
python courier_planner.py
```

Change the capacity or dataset:

```bash
python courier_planner.py --capacity 18
python courier_planner.py --parcels data/parcels.csv --roads data/roads.csv --capacity 15
```

## Input data format

### `data/parcels.csv`

| Field | Meaning |
|---|---|
| `id` | Unique parcel identifier |
| `destination` | Delivery node in the road graph |
| `weight` | Parcel weight in kg |
| `value` | Utility/value score used by knapsack |
| `priority` | Integer priority; larger means more urgent |
| `deadline` | Relative deadline rank; smaller means earlier |

### `data/roads.csv`

An undirected weighted edge list. Each row connects two graph nodes, with `distance`
measured in kilometres. The sample graph uses `DEPOT` as the warehouse.

## Algorithmic complexity

Let `n` be the number of parcels, `W` the capacity in tenths of a kg, `V` the
number of graph vertices, `E` the number of road edges, and `k` the number of
selected unique delivery points.

| Component | Technique | Time complexity |
|---|---|---|
| Prioritization | Merge Sort | `O(n log n)` |
| Packing | 0/1 Knapsack DP | `O(nW)` |
| Single-source shortest paths | Dijkstra + binary heap | `O((V+E) log V)` |
| Route approximation | Nearest neighbor over shortest-path distances | Up to `O(k(V+E) log V + k²)` |
| Runtime benchmark | Repeated measurements | Depends on input and repeat count |

## Design assumptions and limitations

- Road distances are symmetric and non-negative; the sample graph is undirected.
- The packing objective maximizes parcel value subject to vehicle weight capacity.
  Priority/deadline determine processing order; they are not additional knapsack constraints.
- The route visits each distinct destination represented by a selected parcel once.
  Multiple parcels for one destination are delivered at the same stop.
- Dijkstra is run on the road graph. The nearest-neighbor heuristic chooses the next
  destination using these shortest-path distances.
- The prototype does not model time windows, vehicle volume, traffic, multiple vehicles,
  driver breaks, or parcel incompatibilities. Those are suitable extensions.

## Tests

```bash
python -m unittest discover -s tests -v
```

## Regenerate the runtime chart

```bash
python generate_assets.py
```

## Larger-dataset performance test

Run `python benchmark_scaling.py` to generate `charts/runtime_scaling.png`.
It benchmarks 20, 80 and 200 parcels using deterministic synthetic data. Graph size scales with the parcel count; the route heuristic is capped at eight stops to keep the experiment repeatable. These are illustrative local runtimes, not hardware-independent performance guarantees.
