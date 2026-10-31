import tempfile
import unittest
from graphcache import Graph, Node, BackendOptions
from graphcache.scenario import Step, WorkloadReplay

class ReplaySmoke(unittest.TestCase):
    def test_replay_with_single_stable_specialization(self):
        graph = Graph((Node("x", "input"), Node("y", "relu", ("x",))), "y")
        with tempfile.TemporaryDirectory() as d:
            replay = WorkloadReplay(d)
            step = Step(graph, (-1.0, 2.0), 1, 4, BackendOptions())
            self.assertEqual(replay.apply(step), [0, 2.0])
            self.assertEqual(replay.apply(step), [0, 2.0])
            self.assertEqual(replay.history[-1]["compiled"], 1)
