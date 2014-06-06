import unittest
from pyrser import meta
from pyrser import grammar
from pyrser.parsing import functors
from pyrser.passes import to_yml
from pyrser.codegen.c import cython


class GenDsl_Test(unittest.TestCase):
    def test_00_empty_rule(self):
        """Test gen empty_rule
        """
        class Empty(grammar.Grammar):
            entry = "test"
            grammar = """test = [ 'a' ['c' | 'b' ['e' | 'z'] ] 'd']"""
        for k, v in Empty._rules.items():
            if isinstance(v, functors.Functor):
               print("%s:\n %s\n---\n" % (k, str(to_yml.to_yml(v))))
        p = Empty()
        cython.generate(p, 'Empty')
