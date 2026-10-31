"""Historical billing workload replay."""
import json
import tempfile
from graphcache import BackendOptions, Graph, GraphCompiler, Node, ShapeEnvironment, evaluate_reference


def view():
    return Graph((Node('values', 'input'),
                  Node('rate', 'const', attrs={'value': 1.25}),
                  Node('converted', 'mul', ('values', 'rate')),
                  Node('with_fee', 'add', ('converted', 'rate'), {'alpha': 1.75}),
                  Node('window', 'prefix_sum', ('with_fee',), {'limit': 4}),
                  Node('display', 'quantize', ('window',))), 'display')


def main():
    graph = view()
    stages = (([0.25, 0.75], (1, 3), 'nearest', False),
              ([0.25] * 7, (5, 9), 'floor', False),
              ([0.25, 0.75], (1, 3), 'floor', True),
              ([0.25, 0.75], (1, 3), 'nearest', True))
    with tempfile.TemporaryDirectory() as root:
        service = None
        for index, (rows, bounds, mode, restart) in enumerate(stages):
            if service is None or restart:
                service = GraphCompiler(ShapeEnvironment(*bounds), root)
            else:
                service.env.rebind(*bounds)
            settings = BackendOptions(extras={'rounding': mode})
            expected = evaluate_reference(graph, rows, settings)
            try:
                actual = service.run(graph, rows, settings)
                report = dict(step=index, same=actual == expected, actual=actual, expected=expected)
            except Exception as exc:
                report = dict(step=index, same=False, exception=type(exc).__name__)
            print(json.dumps(report, sort_keys=True))


if __name__ == '__main__':
    main()
