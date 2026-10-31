"""Reproduce a mismatch between two compilation histories."""
import tempfile
from graphcache import Graph, Node, GraphCompiler, BackendOptions, ShapeEnvironment, evaluate_reference

def run():
    graph = Graph((Node('x','input'), Node('s','prefix_sum',('x',),{'limit':3}), Node('y','quantize',('s',))), 'y')
    with tempfile.TemporaryDirectory() as root:
        c=GraphCompiler(ShapeEnvironment(1,2),root)
        for bounds,values,rounding in [((1,2),[0.6,1.2],'nearest'),((5,7),[0.6,1.2,2.4,3.1,4.0],'floor'),((1,2),[0.6,1.2],'nearest')]:
            c.env.rebind(*bounds)
            o=BackendOptions(extras={'rounding':rounding})
            expected=evaluate_reference(graph,values,o)
            try: actual=c.run(graph,values,o)
            except Exception as e: actual=type(e).__name__
            print({'bounds':bounds,'rounding':rounding,'expected':expected,'actual':actual})
if __name__=='__main__': run()
