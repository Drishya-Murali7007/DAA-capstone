"""
Intelligent Courier Planner
Algorithms: Merge Sort, 0/1 Knapsack (dynamic programming), Dijkstra,
Nearest-neighbor TSP approximation, and runtime benchmarking.
Run: python courier_planner.py
"""
from __future__ import annotations
import argparse
import csv
import heapq
import json
import math
import random
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"


def load_parcels(path: Path) -> List[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for p in rows:
        p["weight"] = float(p["weight"])
        p["value"] = int(p["value"])
        p["priority"] = int(p["priority"])
        p["deadline"] = int(p["deadline"])
    return rows


def load_graph(path: Path) -> Dict[str, List[Tuple[str, float]]]:
    graph: Dict[str, List[Tuple[str, float]]] = {}
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            a, b, d = row["from"], row["to"], float(row["distance"])
            graph.setdefault(a, []).append((b, d))
            graph.setdefault(b, []).append((a, d))
    return graph


def merge_sort_parcels(parcels: List[dict]) -> List[dict]:
    """Stable merge sort: priority descending, deadline ascending."""
    if len(parcels) <= 1:
        return parcels[:]
    mid = len(parcels) // 2
    left = merge_sort_parcels(parcels[:mid])
    right = merge_sort_parcels(parcels[mid:])
    result, i, j = [], 0, 0
    def key(p):
        return (-p["priority"], p["deadline"], p["id"])
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:]); result.extend(right[j:])
    return result


def knapsack_select(parcels: List[dict], capacity: float):
    """
    0/1 knapsack DP. Weights are converted to integer tenths of kg to keep
    the DP table exact for this dataset format.
    Returns selected parcels, total value, total weight, and DP table.
    """
    scale = 10
    cap = int(round(capacity * scale))
    weights = [int(round(p["weight"] * scale)) for p in parcels]
    n = len(parcels)
    dp = [[0] * (cap + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        w, v = weights[i - 1], parcels[i - 1]["value"]
        for c in range(cap + 1):
            dp[i][c] = dp[i - 1][c]
            if w <= c:
                dp[i][c] = max(dp[i][c], dp[i - 1][c - w] + v)
    selected = []
    c = cap
    for i in range(n, 0, -1):
        if dp[i][c] != dp[i - 1][c]:
            selected.append(parcels[i - 1])
            c -= weights[i - 1]
    selected.reverse()
    return selected, dp[n][cap], sum(p["weight"] for p in selected), dp


def dijkstra(graph: Dict[str, List[Tuple[str, float]]], source: str):
    """Single-source shortest paths using a min-priority queue."""
    distances = {node: math.inf for node in graph}
    previous: Dict[str, Optional[str]] = {node: None for node in graph}
    if source not in graph:
        raise ValueError(f"Unknown source node: {source}")
    distances[source] = 0.0
    heap = [(0.0, source)]
    while heap:
        dist, node = heapq.heappop(heap)
        if dist != distances[node]:
            continue
        for neighbor, cost in graph[node]:
            candidate = dist + cost
            if candidate < distances[neighbor]:
                distances[neighbor] = candidate
                previous[neighbor] = node
                heapq.heappush(heap, (candidate, neighbor))
    return distances, previous


def reconstruct_path(previous, target: str):
    if target not in previous:
        return []
    path, node = [], target
    while node is not None:
        path.append(node)
        node = previous[node]
    return list(reversed(path))


def nearest_neighbor_route(graph, depot: str, destinations: List[str]):
    """
    TSP approximation over shortest-path distances. At each step, visit the
    unvisited delivery point with the smallest shortest-path distance.
    Returns visit order, expanded road path, and total distance including return.
    """
    if depot not in graph:
        raise ValueError(f"Unknown depot: {depot}")
    targets = list(dict.fromkeys(destinations))
    targets = [x for x in targets if x != depot]
    current, remaining = depot, set(targets)
    order, full_path, total = [depot], [depot], 0.0
    cache = {}
    while remaining:
        if current not in cache:
            cache[current] = dijkstra(graph, current)
        dist, prev = cache[current]
        nxt = min(remaining, key=lambda x: (dist.get(x, math.inf), x))
        if math.isinf(dist.get(nxt, math.inf)):
            raise ValueError(f"No route from {current} to {nxt}")
        segment = reconstruct_path(prev, nxt)
        total += dist[nxt]
        full_path.extend(segment[1:])
        order.append(nxt)
        remaining.remove(nxt)
        current = nxt
    dist, prev = dijkstra(graph, current)
    if depot not in dist or math.isinf(dist[depot]):
        raise ValueError(f"No return route from {current} to {depot}")
    segment = reconstruct_path(prev, depot)
    total += dist[depot]
    full_path.extend(segment[1:])
    order.append(depot)
    return order, full_path, total


def benchmark(parcels, graph, repeats=5):
    """Measure sorting, knapsack, Dijkstra and route planning; times in ms."""
    results = {}
    destinations = sorted([n for n in graph if n != "DEPOT"])
    capacity = 15.0
    operations = {
        "Merge sort": lambda: merge_sort_parcels(parcels),
        "Knapsack DP": lambda: knapsack_select(merge_sort_parcels(parcels), capacity),
        "Dijkstra": lambda: dijkstra(graph, "DEPOT"),
        "Nearest-neighbor route": lambda: nearest_neighbor_route(graph, "DEPOT", destinations),
    }
    for name, fn in operations.items():
        samples = []
        for _ in range(repeats):
            start = time.perf_counter()
            fn()
            samples.append((time.perf_counter() - start) * 1000)
        results[name] = sum(samples) / len(samples)
    return results


def run(parcels_path=DATA / "parcels.csv", roads_path=DATA / "roads.csv", capacity=15.0):
    parcels = load_parcels(Path(parcels_path))
    graph = load_graph(Path(roads_path))
    ordered = merge_sort_parcels(parcels)
    selected, value, weight, dp = knapsack_select(ordered, capacity)
    selected_stops = sorted(set(p["destination"] for p in selected))
    route_order, road_path, route_distance = nearest_neighbor_route(graph, "DEPOT", selected_stops)

    print("\n" + "=" * 68)
    print("                 INTELLIGENT COURIER PLANNER")
    print("=" * 68)
    print(f"Vehicle capacity: {capacity:.1f} kg")
    print("\n1) PARCEL PRIORITIZATION (priority descending, deadline ascending)")
    print(f"{'ID':<8}{'Destination':<15}{'Weight':>9}{'Value':>9}{'Priority':>11}{'Deadline':>11}")
    for p in ordered:
        print(f"{p['id']:<8}{p['destination']:<15}{p['weight']:>9.1f}{p['value']:>9}{p['priority']:>11}{p['deadline']:>11}")
    print("\n2) OPTIMAL BOX FILLING (0/1 knapsack)")
    print("Selected:", ", ".join(p["id"] for p in selected) or "None")
    print(f"Packed weight: {weight:.1f}/{capacity:.1f} kg | Total value: {value}")
    print("DP evidence: final capacity row (sampled every 1 kg):")
    final_row = dp[-1]
    print(" ".join(str(final_row[min(i * 10, len(final_row)-1)]) for i in range(int(capacity)+1)))
    print("\n3) DELIVERY ROUTE")
    print("Visit order:", " -> ".join(route_order))
    print("Expanded road path:", " -> ".join(road_path))
    print(f"Total route distance (including return): {route_distance:.1f} km")
    print("\n4) PERFORMANCE (mean of 5 runs)")
    timings = benchmark(parcels, graph)
    for name, ms in timings.items():
        print(f"{name:<28} {ms:>10.4f} ms")
    print("=" * 68)
    return {"ordered": ordered, "selected": selected, "value": value, "weight": weight,
            "route_order": route_order, "road_path": road_path,
            "route_distance": route_distance, "timings": timings}


def main():
    parser = argparse.ArgumentParser(description="Intelligent Courier Planner")
    parser.add_argument("--parcels", default=str(DATA / "parcels.csv"))
    parser.add_argument("--roads", default=str(DATA / "roads.csv"))
    parser.add_argument("--capacity", type=float, default=15.0)
    args = parser.parse_args()
    run(args.parcels, args.roads, args.capacity)

if __name__ == "__main__":
    main()
