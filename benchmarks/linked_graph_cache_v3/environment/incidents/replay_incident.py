"""Public incident replay; shows observations but does not diagnose them."""
from __future__ import annotations

import json
import tempfile

from graphcache import (
    BackendOptions, Graph, Node, GraphCompiler, ShapeEnvironment, evaluate_reference
)


def main():
    graph = Graph((
        Node("input", "input"),
        Node("weight", "const", attrs={"value": 1.25}),
        Node("product", "mul", ("input", "weight")),
        Node("sum", "add", ("product", "weight"), {"alpha": 1.0}),
        Node("window", "prefix_sum", ("sum",), {"limit": 3}),
        Node("output", "quantize", ("window",)),
    ), "output")

    examples = [
        ((0.3, 1.2), (1, 2), "nearest", False),
        ((0.3, 1.2, 2.3, 3.4, 4.5, 5.6, 6.7), (5, 9), "floor", False),
        ((0.3, 1.2), (1, 2), "nearest", True),
        ((0.3, 1.2, 2.3, 3.4, 4.5, 5.6, 6.7), (5, 9), "floor", True),
    ]

    with tempfile.TemporaryDirectory() as directory:
        compiler = None
        for index, (values, bounds, rounding, restart) in enumerate(examples):
            if compiler is None or restart:
                compiler = GraphCompiler(ShapeEnvironment(*bounds), directory)
            else:
                compiler.env.rebind(*bounds)
            options = BackendOptions(extras={"rounding": rounding})
            expected = evaluate_reference(graph, list(values), options)
            record = {
                "step": index,
                "shape": len(values),
                "bounds": list(bounds),
                "rounding": rounding,
                "restart": restart,
                "expected": expected,
            }
            try:
                record["observed"] = compiler.run(graph, list(values), options)
                record["matches"] = record["observed"] == expected
            except Exception as error:
                record["exception"] = type(error).__name__
                record["matches"] = False
            print(json.dumps(record, sort_keys=True))


if __name__ == "__main__":
    main()
