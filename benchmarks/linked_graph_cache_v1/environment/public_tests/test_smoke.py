"""Public smoke tests (the initial faulty version should pass)."""
import tempfile
import unittest
from graphcache import BackendOptions, Graph, Node, GraphCompiler, ShapeEnvironment, evaluate_reference

def graph_add_mul(alpha=1.0):
    return Graph((Node("x", "input"), Node("c", "const", attrs={"value": 2.0}),
                  Node("m", "mul", ("x", "c")),
                  Node("out", "add", ("m", "c"), {"alpha": alpha})), "out")

def graph_prefix(limit=6):
    return Graph((Node("x", "input"), Node("s", "prefix_sum", ("x",), {"limit": limit})), "s")

def graph_quantize():
    return Graph((Node("x", "input"), Node("out", "quantize", ("x",))), "out")

class SmokeTests(unittest.TestCase):
    def test_default_fusion(self):
        g = graph_add_mul()
        self.assertEqual(GraphCompiler().run(g, [1.0, 2.0]), evaluate_reference(g, [1.0, 2.0]))

    def test_one_shape_specialization(self):
        g = graph_prefix()
        self.assertEqual(GraphCompiler(ShapeEnvironment(1, 4)).run(g, [1, 2, 3]), 6)

    def test_cache_reuses_matching_workload(self):
        with tempfile.TemporaryDirectory() as d:
            compiler = GraphCompiler(ShapeEnvironment(1, 8), d)
            g = graph_quantize()
            options = BackendOptions(extras={"rounding": "nearest"})
            self.assertEqual(compiler.run(g, [0.2, 0.8], options), [0, 1])
            self.assertEqual(compiler.run(g, [0.2, 0.8], options), [0, 1])
            self.assertEqual(compiler.compile_count, 1)
            self.assertGreaterEqual(compiler.cache.hits, 1)

if __name__ == "__main__":
    unittest.main()
