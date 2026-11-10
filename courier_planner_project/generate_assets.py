from pathlib import Path
import sys, random, time
import matplotlib.pyplot as plt
sys.path.insert(0, str(Path(__file__).resolve().parent))
from courier_planner import load_parcels, load_graph, benchmark, merge_sort_parcels, knapsack_select, dijkstra, nearest_neighbor_route

ROOT = Path(__file__).resolve().parent
parcels = load_parcels(ROOT / "data/parcels.csv")
graph = load_graph(ROOT / "data/roads.csv")
timings = benchmark(parcels, graph, repeats=20)

# Repeated benchmark on the supplied small dataset.
names = list(timings)
values = [timings[n] for n in names]
plt.figure(figsize=(9, 5))
bars = plt.bar(names, values)
plt.ylabel("Mean runtime (milliseconds)")
plt.title("Courier Planner — Component Runtime (20-run mean)")
plt.xticks(rotation=15, ha="right")
plt.grid(axis="y", alpha=.25)
for bar, val in zip(bars, values):
    plt.text(bar.get_x()+bar.get_width()/2, bar.get_height(), f"{val:.4f}", ha="center", va="bottom", fontsize=8)
plt.tight_layout()
plt.savefig(ROOT / "charts" / "runtime_comparison.png", dpi=180)
plt.close()

# A compact terminal-like screenshot based on a fresh execution.
import subprocess
result = subprocess.run([sys.executable, str(ROOT / "courier_planner.py")], cwd=ROOT, capture_output=True, text=True)
lines = result.stdout.strip().splitlines()
# Keep all output; wrap in a legible terminal-style figure.
fig_h = max(7, len(lines) * 0.22)
fig = plt.figure(figsize=(13, fig_h))
fig.patch.set_facecolor("#10131a")
ax = fig.add_axes([0.025, 0.02, 0.95, 0.96])
ax.set_facecolor("#10131a")
ax.axis("off")
ax.text(0.015, 0.99, "\n".join(lines), va="top", ha="left",
        family="monospace", fontsize=9, color="#e8edf5", linespacing=1.35)
plt.savefig(ROOT / "screenshots" / "sample_output.png", dpi=150, facecolor=fig.get_facecolor(), bbox_inches="tight")
plt.close()
print("Generated charts/runtime_comparison.png and screenshots/sample_output.png")
