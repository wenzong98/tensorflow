"""Unoptimized, independent execution semantics for this task's graph language.

The semantics here are deliberately explicit and stable. Compiled output is
compared against this interpreter, not against the candidate optimizer.
"""
from __future__ import annotations
import math
from .ir import Graph


def _pairwise(a, b, action):
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            raise ValueError("length mismatch")
        return [action(x, y) for x, y in zip(a, b)]
    if isinstance(a, list):
        return [action(x, b) for x in a]
    if isinstance(b, list):
        return [action(a, y) for y in b]
    return action(a, b)


def _unary(a, action):
    return [action(v) for v in a] if isinstance(a, list) else action(a)


def run_graph(graph: Graph, values: list[float], rounding: str = "nearest"):
    state = {}
    for node in graph.nodes:
        a = [state[k] for k in node.args]
        if node.op == "input":
            result = list(values)
        elif node.op == "const":
            result = node.attrs["value"]
        elif node.op == "add":
            alpha = node.attrs.get("alpha", 1.0)
            result = _pairwise(a[0], a[1], lambda x, y: x + alpha * y)
        elif node.op == "mul":
            result = _pairwise(a[0], a[1], lambda x, y: x * y)
        elif node.op == "fma":
            result = _pairwise(_pairwise(a[0], a[1], lambda x, y: x * y), a[2], lambda x, y: x + y)
        elif node.op == "relu":
            result = _unary(a[0], lambda x: x if x > 0 else 0)
        elif node.op == "prefix_sum":
            result = sum(a[0][:node.attrs["limit"]])
        elif node.op == "prefix_sum_all":
            result = sum(a[0])
        elif node.op == "prefix_sum_fixed":
            result = sum(a[0][:node.attrs["count"]])
        elif node.op in {"quantize", "round_nearest", "round_floor"}:
            mode = rounding if node.op == "quantize" else node.op.removeprefix("round_")
            if mode not in {"floor", "nearest"}:
                raise ValueError("unsupported rounding: " + mode)
            result = _unary(a[0], lambda x: math.floor(x) if mode == "floor" else math.floor(x + 0.5))
        else:
            raise ValueError("unknown op: " + node.op)
        state[node.name] = result
    return state[graph.output]


def evaluate_reference(graph, values, options=None):
    extras = getattr(options, "extras", None) or {}
    return run_graph(graph, values, extras.get("rounding", "nearest"))
