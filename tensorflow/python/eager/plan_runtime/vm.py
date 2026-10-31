"""Execute compiled register programs without the reference interpreter."""
from __future__ import annotations
import math
from .bytecode import BYTECODE_VERSION, Bytecode

def _binary(a, b, func, width):
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            raise ValueError("length mismatch")
        return [func(a[i], b[i]) for k in range(0, len(a), width)
                for i in range(k, min(k + width, len(a)))]
    if isinstance(a, list):
        return [func(a[i], b) for k in range(0, len(a), width)
                for i in range(k, min(k + width, len(a)))]
    if isinstance(b, list):
        return [func(a, b[i]) for k in range(0, len(b), width)
                for i in range(k, min(k + width, len(b)))]
    return func(a, b)

def _unary(a, fn, width):
    if isinstance(a, list):
        return [fn(a[i]) for k in range(0, len(a), width)
                for i in range(k, min(k + width, len(a)))]
    return fn(a)

class RegisterVM:
    def __init__(self, program: Bytecode):
        if program.version != BYTECODE_VERSION:
            raise ValueError("invalid bytecode ABI")
        if program.vector_width not in (1, 2, 4, 8):
            raise ValueError("invalid vector width")
        if not (0 <= program.output_register < program.register_count):
            raise ValueError("invalid output register")
        self.program = program

    def execute(self, values):
        regs = [None] * self.program.register_count
        width = self.program.vector_width
        for row in self.program.instructions:
            op, dst, *args = row
            if op == "INPUT":
                result = list(values)
            elif op == "CONST":
                result = args[0]
            elif op == "ADD":
                x, y, alpha = args
                result = _binary(regs[x], regs[y], lambda a, b: a + alpha * b, width)
            elif op == "MUL":
                x, y = args
                result = _binary(regs[x], regs[y], lambda a, b: a * b, width)
            elif op == "FMA":
                x, y, z = args
                result = _binary(_binary(regs[x], regs[y], lambda a, b: a * b, width),
                                 regs[z], lambda a, b: a + b, width)
            elif op == "RELU":
                result = _unary(regs[args[0]], lambda a: a if a > 0 else 0, width)
            elif op == "SUM_ALL":
                result = sum(regs[args[0]])
            elif op == "PREFIX":
                result = sum(regs[args[0]][:int(args[1])])
            elif op == "ROUND":
                x, rounding = args
                if rounding not in ("floor", "nearest"):
                    raise ValueError("invalid rounding mode")
                fn = math.floor if rounding == "floor" else lambda a: math.floor(a + 0.5)
                result = _unary(regs[x], fn, width)
            else:
                raise ValueError("invalid instruction")
            regs[dst] = result
        return regs[self.program.output_register]
