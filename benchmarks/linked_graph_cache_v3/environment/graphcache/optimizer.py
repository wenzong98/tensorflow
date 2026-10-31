"""Local expression rewriting and specialization of shape-dependent operators."""
from .ir import Graph, Node


def optimize(graph: Graph, env, options):
    by_name = {}
    replace = {}
    new_nodes = []
    for node in graph.nodes:
        current = node
        if node.op == "prefix_sum":
            mode, count = env.classify_prefix(node.attrs["limit"])
            if mode == "all":
                current = Node(node.name, "prefix_sum_all", node.args)
            elif mode == "fixed":
                current = Node(node.name, "prefix_sum_fixed", node.args, {"count": count})
        elif node.op == "quantize":
            mode = options.extras.get("rounding", "nearest")
            if mode not in {"floor", "nearest"}:
                raise ValueError("invalid rounding mode")
            current = Node(node.name, "round_" + mode, node.args)
        elif node.op == "add" and len(node.args) == 2:
            # Fuse add(mul(a, b), c) into fma(a, b, c).
            left_name, right_name = node.args
            left = by_name.get(left_name)
            right = by_name.get(right_name)
            if left and left.op == "mul":
                current = Node(node.name, "fma", (left.args[0], left.args[1], right_name))
            elif right and right.op == "mul":
                current = Node(node.name, "fma", (right.args[0], right.args[1], left_name))
        new_nodes.append(current)
        by_name[node.name] = current
    return Graph(tuple(new_nodes), graph.output)
