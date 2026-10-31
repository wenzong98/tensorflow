import unittest
from graphcache import Graph, Node, BackendOptions, ShapeEnvironment
from graphcache.contract import CompilationContract
from graphcache.cache import CACHE_ABI

class ContractSmoke(unittest.TestCase):
    def test_identity_is_stable_for_unchanged_inputs(self):
        g=Graph((Node('x','input'),),'x')
        o=BackendOptions()
        e=ShapeEnvironment(1,4)
        a=CompilationContract.capture(g,o,e,CACHE_ABI)
        b=CompilationContract.capture(g,o,e,CACHE_ABI)
        self.assertEqual(a.identity(),b.identity())
        self.assertTrue(a.same_compilation(b))
