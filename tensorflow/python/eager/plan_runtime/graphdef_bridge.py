"""Adapter from a supported numeric GraphDef subset to report plans."""
from __future__ import annotations
import struct
from .ir import Graph, Node

def _strip_tensor_name(name):
    return name.lstrip('^').split(':', 1)[0]

def _tensor_scalar(tensor):
    for field in ('double_val', 'float_val', 'int_val', 'int64_val'):
        xs = getattr(tensor, field, None)
        if xs:
            return xs[0]
    raw = getattr(tensor, 'tensor_content', b'')
    dtype = int(getattr(tensor, 'dtype', 0))
    formats = {1: 'f', 2: 'd', 3: 'i', 9: 'q'}
    fmt = formats.get(dtype)
    if fmt and len(raw) >= struct.calcsize('<' + fmt):
        return struct.unpack_from('<' + fmt, raw)[0]
    raise ValueError('only numeric scalar constants are supported')

def from_graph_def(graph_def, output, input_name=None):
    """Convert a topologically ordered subset of GraphDef to a numeric Graph."""
    output = _strip_tensor_name(output)
    alias, nodes = {}, []
    for item in graph_def.node:
        deps = [_strip_tensor_name(x) for x in item.input if not x.startswith('^')]
        resolved = tuple(alias.get(dep, dep) for dep in deps)
        op = item.op
        if op in ('Placeholder', 'PlaceholderV2'):
            if input_name is not None and item.name != input_name:
                raise ValueError('graph has unsupported additional placeholder')
            node = Node(item.name, 'input')
        elif op == 'Const':
            node = Node(item.name, 'const', attrs={'value': _tensor_scalar(item.attr['value'].tensor)})
        elif op in ('Add', 'AddV2'):
            node = Node(item.name, 'add', resolved)
        elif op == 'Mul':
            node = Node(item.name, 'mul', resolved)
        elif op == 'Relu':
            node = Node(item.name, 'relu', resolved)
        elif op == 'Identity':
            if len(resolved) != 1:
                raise ValueError('identity requires one input')
            alias[item.name] = resolved[0]
            continue
        else:
            raise ValueError('unsupported GraphDef op: ' + op)
        nodes.append(node)
    return Graph(tuple(nodes), alias.get(output, output))
