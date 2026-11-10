import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from courier_planner import merge_sort_parcels, knapsack_select, dijkstra, reconstruct_path, nearest_neighbor_route

class CourierPlannerTests(unittest.TestCase):
    def test_sorting(self):
        data = [
            {"id":"x","priority":2,"deadline":1},
            {"id":"b","priority":5,"deadline":3},
            {"id":"a","priority":5,"deadline":1},
        ]
        self.assertEqual([p["id"] for p in merge_sort_parcels(data)], ["a","b","x"])

    def test_knapsack(self):
        data = [
            {"id":"a","weight":2.0,"value":3},
            {"id":"b","weight":3.0,"value":4},
            {"id":"c","weight":4.0,"value":5},
        ]
        selected, value, weight, _ = knapsack_select(data, 5.0)
        self.assertEqual(value, 7)
        self.assertAlmostEqual(weight, 5.0)
        self.assertEqual({p["id"] for p in selected}, {"a","b"})

    def test_dijkstra(self):
        graph = {"S":[("A",2),("B",8)], "A":[("S",2),("B",1)], "B":[("S",8),("A",1)]}
        dist, prev = dijkstra(graph, "S")
        self.assertEqual(dist["B"], 3)
        self.assertEqual(reconstruct_path(prev, "B"), ["S","A","B"])

    def test_route(self):
        graph = {"DEPOT":[("A",2),("B",5)], "A":[("DEPOT",2),("B",1)], "B":[("DEPOT",5),("A",1)]}
        order, path, distance = nearest_neighbor_route(graph, "DEPOT", ["A","B"])
        self.assertEqual(order[0], "DEPOT")
        self.assertEqual(order[-1], "DEPOT")
        self.assertGreater(distance, 0)
        self.assertEqual(path[0], "DEPOT")

if __name__ == "__main__":
    unittest.main()
