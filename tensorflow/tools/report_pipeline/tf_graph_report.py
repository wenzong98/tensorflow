"""Run numeric report operations on a serialized TensorFlow GraphDef."""
import argparse
import json

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('graphdef', help='serialized TensorFlow GraphDef file')
    parser.add_argument('--output', required=True)
    parser.add_argument('--input', dest='input_name', required=True)
    parser.add_argument('--values', required=True, help='JSON numeric vector')
    parser.add_argument('--cache-dir', default=None)
    args = parser.parse_args()
    from tensorflow.core.framework import graph_pb2
    from tensorflow.python.eager.plan_runtime.graphdef_bridge import from_graph_def
    from tensorflow.python.eager.plan_runtime.compiler import GraphCompiler
    from tensorflow.python.eager.plan_runtime.shape import ShapeEnvironment
    graph = graph_pb2.GraphDef()
    with open(args.graphdef, 'rb') as input_file:
        graph.ParseFromString(input_file.read())
    program = from_graph_def(graph, args.output, args.input_name)
    values = json.loads(args.values)
    service = GraphCompiler(ShapeEnvironment(1, max(1, len(values))), args.cache_dir)
    print(json.dumps(service.run(program, values)))

if __name__ == '__main__':
    main()
