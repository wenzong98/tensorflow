"""Memory and disk specialization cache with persisted ABI metadata."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from dataclasses import dataclass
from .ir import Graph
from .contract import CompilationContract

CACHE_ABI = "graphcache-compiler-v2"


@dataclass(frozen=True)
class Artifact:
    original_graph: str
    graph: Graph
    options: dict
    lower: int
    upper: int
    compiler_abi: str = CACHE_ABI
    bytecode: dict | None = None

    def to_dict(self):
        return {"original_graph": self.original_graph,
                "graph": self.graph.to_dict(), "options": self.options,
                "lower": self.lower, "upper": self.upper,
                "compiler_abi": self.compiler_abi, "bytecode": self.bytecode}

    @staticmethod
    def from_dict(value):
        return Artifact(value["original_graph"], Graph.from_dict(value["graph"]),
                        dict(value["options"]), value["lower"], value["upper"],
                        value.get("compiler_abi", "legacy-v0"), value.get("bytecode"))


class SpecializationCache:
    def __init__(self, path=None):
        self.path = Path(path) if path is not None else None
        if self.path:
            self.path.mkdir(parents=True, exist_ok=True)
        self._memory = {}
        self.hits = 0
        self.misses = 0

    @staticmethod
    def _filename(key):
        return hashlib.sha256(key.encode("utf-8")).hexdigest() + ".json"

    @staticmethod
    def _accept(artifact: Artifact, size: int):
        return size >= artifact.lower

    def get(self, key, size, contract=None):
        for artifact in self._memory.get(key, ()):
            if self._accept(artifact, size) and (contract is None or contract.guard(size)):
                self.hits += 1
                return artifact
        if self.path:
            file = self.path / self._filename(key)
            if file.exists():
                try:
                    with file.open(encoding="utf-8") as handle:
                        data = json.load(handle)
                    candidate = Artifact.from_dict(data)
                    if self._accept(candidate, size):
                        self._memory.setdefault(key, []).append(candidate)
                        self.hits += 1
                        return candidate
                except (OSError, ValueError, TypeError, KeyError):
                    pass
        self.misses += 1
        return None

    def put(self, key, artifact: Artifact, contract=None):
        self._memory.setdefault(key, []).append(artifact)
        if self.path:
            file = self.path / self._filename(key)
            file.write_text(json.dumps(artifact.to_dict(), sort_keys=True), encoding="utf-8")
