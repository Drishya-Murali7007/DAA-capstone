from pathlib import Path
import random, time, math
import matplotlib.pyplot as plt
from courier_planner import merge_sort_parcels, knapsack_select, dijkstra, nearest_neighbor_route

ROOT = Path(__file__).resolve().parent
random.seed(7)

def make_parcels(n):
    return [{"id": f"X{i:04d}", "weight": random.choice([0.5,1,1.5,2,2.5,3]),
             "value": random.randint(10,200), "priority": random.randint(1,5),
             "deadline": random.randint(1,10), "destination": f"N{i%max(3,n//2):03d}"}
            for i in range(n)]

def make_graph(n):
    g = {f"N{i:03d}": [] for i in range(n)}
    # Ring guarantees connectivity; extra edges create alternate paths.
    for i in range(n):
        a, b = f"N{i:03d}", f"N{(i+1)%n:03d}"
        g[a].append((b, random.randint(1,12)))
        g[b].append((a, g[a][-1][1]))
    for _ in range(n * 2):
        i, j = random.sample(range(n), 2)
        a, b, w = f"N{i:03d}", f"N{j:03d}", random.randint(1,20)
        g[a].append((b,w)); g[b].append((a,w))
    return g

def measure(fn, repeats=3):
    vals=[]
    for _ in range(repeats):
        t=time.perf_counter(); fn(); vals.append((time.perf_counter()-t)*1000)
    return sum(vals)/len(vals)

sizes=[20, 80, 200]
sort_ms=[]; dp_ms=[]; dij_ms=[]; route_ms=[]
for n in sizes:
    ps=make_parcels(n)
    cap=max(20, n//2)  # kg, DP capacity is stored in tenths internally
    graph=make_graph(max(8, n//4))
    nodes=sorted(graph)
    sort_ms.append(measure(lambda: merge_sort_parcels(ps)))
    dp_ms.append(measure(lambda: knapsack_select(ps, cap)))
    dij_ms.append(measure(lambda: dijkstra(graph, nodes[0])))
    # Bound the route size for a readable, repeatable heuristic benchmark.
    route_nodes=nodes[:min(8, len(nodes))]
    route_ms.append(measure(lambda: nearest_neighbor_route(graph, nodes[0], route_nodes)))

plt.figure(figsize=(9,5))
for label, vals in [("Merge Sort",sort_ms),("Knapsack DP",dp_ms),("Dijkstra",dij_ms),("Nearest-neighbor route",route_ms)]:
    plt.plot(sizes, vals, marker="o", linewidth=2, label=label)
plt.xlabel("Number of parcels (graph size scales with dataset)")
plt.ylabel("Mean runtime (milliseconds, 3 runs)")
plt.title("Runtime Scaling — Synthetic Small and Larger Datasets")
plt.grid(alpha=.25); plt.legend()
plt.tight_layout()
plt.savefig(ROOT/"charts"/"runtime_scaling.png", dpi=180)
plt.close()
print("Scaling benchmark (ms):")
for i,n in enumerate(sizes):
    print(n, f"sort={sort_ms[i]:.4f}", f"knapsack={dp_ms[i]:.4f}",
          f"dijkstra={dij_ms[i]:.4f}", f"route={route_ms[i]:.4f}")
