"""Compilation identity and artifact admissibility projections.

A single compilation has several views: the caller's mutable inputs, a
shape-analysis environment, an optimized graph, and a durable cache record.
These helpers are the current shared contract used across those views.
"""
from __future__ import annotations
from dataclasses import dataclass
import json

@dataclass(frozen=True)
class CompilationContract:
    graph_digest: str
    backend: str
    shape_lower: int
    shape_upper: int
    epoch: int
    abi: str

    @staticmethod
    def capture(graph, options, env, abi):
        return CompilationContract(graph.digest(), options.identity(), env.lower,
                                   env.upper, env.epoch, abi)

    def identity(self):
        return self.graph_digest + ':' + self.backend

    def guard(self, size):
        return size >= self.shape_lower

    def same_compilation(self, other):
        return self.identity() == other.identity()

    def to_dict(self):
        return dict(graph_digest=self.graph_digest, backend=self.backend,
                    shape_lower=self.shape_lower, shape_upper=self.shape_upper,
                    epoch=self.epoch, abi=self.abi)

    @classmethod
    def from_dict(cls, obj):
        return cls(**obj)
