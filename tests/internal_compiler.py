import unittest
from pyrser import parsing
from pyrser import meta
from pyrser import error
from pyrser.parsing.functors import *
from pyrser.codegen import compiler as c
import os

from pyrser.passes.to_yml import *

class InternalCompiler_Test(unittest.TestCase):
    def test_01_(self):
        """
        Test default
        """
        # TODO: do it from pure Functors object...
        Functor.auto_skip_ignore = False
        Seq = {'the_rule' : 
            parsing.Seq(
                parsing.Rule('a'),
                parsing.Rule('b'),
                parsing.Rule('c')
            )
        }
        t = c.Transform()
        t.transform(Seq)
        print(str(to_yml(Seq)))
