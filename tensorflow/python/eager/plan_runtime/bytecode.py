"""Lower normalized execution graphs to register programs."""
from __future__ import annotations
from dataclasses import dataclass
BYTECODE_VERSION = 3

@dataclass(frozen=True)
class Bytecode:
    instructions: tuple
    register_count: int
    output_register: int
    vector_width: int
    version: int = BYTECODE_VERSION

    def to_dict(self):
        return {"instructions": [list(op) for op in self.instructions],
                "register_count": self.register_count,
                "output_register": self.output_register,
                "vector_width": self.vector_width, "version": self.version}

    @staticmethod
    def from_dict(obj):
        return Bytecode(tuple(tuple(op) for op in obj["instructions"]),
                        int(obj["register_count"]), int(obj["output_register"]),
                        int(obj["vector_width"]), int(obj.get("version", -1)))

def lower(graph, backend_options):
    """Generate a register program from a topologically ordered graph."""
    if backend_options.get("target") != "cpu":
        raise ValueError("unsupported backend")
    width = backend_options.get("vector_width", 4)
    if width not in (1, 2, 4, 8):
        raise ValueError("unsupported vector width")
    extras = backend_options.get("extras", {})
    rounding = extras.get("rounding", "nearest")
    if rounding not in ("floor", "nearest"):
        raise ValueError("invalid rounding mode")
    readers = {n.name: 0 for n in graph.nodes}
    for n in graph.nodes:
        for input_name in n.args:
            readers[input_name] += 1
    readers[graph.output] += 1
    instructions, slots, free, allocated = [], {}, [], 0
    for n in graph.nodes:
        input_slots = [slots[a] for a in n.args]
        if free:
            slot = free.pop()
        else:
            slot = allocated
            allocated += 1
        if n.op == "input":
            instruction = ("INPUT", slot)
        elif n.op == "const":
            instruction = ("CONST", slot, n.attrs["value"])
        elif n.op == "add":
            instruction = ("ADD", slot, *input_slots, n.attrs.get("alpha", 1.0))
        elif n.op == "mul":
            instruction = ("MUL", slot, *input_slots)
        elif n.op == "fma":
            instruction = ("FMA", slot, *input_slots)
        elif n.op == "relu":
            instruction = ("RELU", slot, *input_slots)
        elif n.op == "prefix_sum":
            instruction = ("PREFIX", slot, *input_slots, n.attrs["limit"])
        elif n.op == "prefix_sum_all":
            instruction = ("SUM_ALL", slot, *input_slots)
        elif n.op == "prefix_sum_fixed":
            instruction = ("PREFIX", slot, *input_slots, n.attrs["count"])
        elif n.op in ("quantize", "round_nearest", "round_floor"):
            mode = rounding if n.op == "quantize" else n.op.removeprefix("round_")
            instruction = ("ROUND", slot, *input_slots, mode)
        else:
            raise ValueError("unknown operation: " + n.op)
        instructions.append(instruction)
        slots[n.name] = slot
        for name in n.args:
            readers[name] -= 1
            if readers[name] == 0:
                free.append(slots[name])
    return Bytecode(tuple(instructions), allocated, slots[graph.output], width)
