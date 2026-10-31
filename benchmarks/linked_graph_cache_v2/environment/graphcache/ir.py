"""Portable graph intermediate representation and stable serialization."""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import json

@dataclass(frozen=True)
class Node:
    name: str
    op: str
    args: tuple[str, ...] = ()
    attrs: dict = field(default_factory=dict)

    def to_dict(self):
        return {"name": self.name, "op": self.op, "args": list(self.args), "attrs": self.attrs}

    @staticmethod
    def from_dict(value):
        return Node(value["name"], value["op"], tuple(value.get("args", [])), dict(value.get("attrs", {})))

@dataclass(frozen=True)
class Graph:
    nodes: tuple[Node, ...]
    output: str

    def __post_init__(self):
        names = set()
        for node in self.nodes:
            if node.name in names:
                raise ValueError("duplicate node: " + node.name)
            if any(dep not in names for dep in node.args):
                raise ValueError("graph must be topologically sorted")
            names.add(node.name)
        if self.output not in names:
            raise ValueError("invalid output")

    def to_dict(self):
        return {"nodes": [node.to_dict() for node in self.nodes], "output": self.output}

    @staticmethod
    def from_dict(value):
        return Graph(tuple(Node.from_dict(x) for x in value["nodes"]), value["output"])

    def digest(self):
        encoded = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()
