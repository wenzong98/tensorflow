"""Specialization compiler joining shape inference, graph rewriting and caches."""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from .shape import ShapeEnvironment
from .optimizer import optimize
from .reference import run_graph
from .cache import Artifact, SpecializationCache

@dataclass(frozen=True)
class BackendOptions:
    target: str = "cpu"
    vector_width: int = 4
    extras: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.target != "cpu" or self.vector_width not in (1, 2, 4, 8):
            raise ValueError("unsupported backend options")

    def identity(self):
        # Persisted backend settings may differ from candidate identity.
        return json.dumps({"target": self.target, "vector_width": self.vector_width}, sort_keys=True)

    def to_dict(self):
        return {"target": self.target, "vector_width": self.vector_width, "extras": self.extras}

class GraphCompiler:
    def __init__(self, env=None, cache_dir=None):
        self.env = env or ShapeEnvironment()
        self.cache = SpecializationCache(cache_dir)
        self.compile_count = 0

    def compile(self, graph, values, options=None, *, force_recompile=False):
        options = options or BackendOptions()
        size = len(values)
        if not self.env.lower <= size <= self.env.upper:
            raise ValueError("input shape is outside active shape environment")
        key = graph.digest() + ":" + options.identity()
        artifact = None if force_recompile else self.cache.get(key, size)
        if artifact is None:
            rewritten = optimize(graph, self.env, options)
            artifact = Artifact(graph.digest(), rewritten, options.to_dict(), self.env.lower, self.env.upper)
            self.cache.put(key, artifact)
            self.compile_count += 1
        return CompiledProgram(artifact)

    def run(self, graph, values, options=None, *, force_recompile=False):
        program = self.compile(graph, values, options, force_recompile=force_recompile)
        return program(values)

class CompiledProgram:
    def __init__(self, artifact):
        self.artifact = artifact

    def __call__(self, values):
        if not self.artifact.lower <= len(values) <= self.artifact.upper:
            raise ValueError("compiled specialization guard violated")
        return run_graph(self.artifact.graph, values)
