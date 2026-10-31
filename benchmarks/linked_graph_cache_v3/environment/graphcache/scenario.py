"""Workload replay across shape epochs and process-like compiler restarts.
Used as public diagnostic utility, not a correctness oracle.
"""
from dataclasses import dataclass
from .compiler import GraphCompiler, BackendOptions
from .shape import ShapeEnvironment

@dataclass(frozen=True)
class Step:
    graph: object
    values: tuple
    lower: int
    upper: int
    options: BackendOptions
    restart: bool = False

class WorkloadReplay:
    def __init__(self, cache_dir=None):
        self.cache_dir = cache_dir
        self.compiler = None
        self.history = []

    def apply(self, step):
        if self.compiler is None or step.restart:
            self.compiler = GraphCompiler(ShapeEnvironment(step.lower, step.upper), self.cache_dir)
        else:
            self.compiler.env.rebind(step.lower, step.upper)
        result = self.compiler.run(step.graph, list(step.values), step.options)
        self.history.append({
            "result": result, "range": [step.lower, step.upper],
            "restart": step.restart, "cache_hits": self.compiler.cache.hits,
            "compiled": self.compiler.compile_count,
        })
        return result
