import unittest
import os
from pyrser import grammar
from pyrser import meta
from pyrser import parsing
from pyrser import error
from pyrser.passes.to_yml import *
from pyrser.directives import ignore
from pyrser.hooks.set import *

class Hooks_Test(unittest.TestCase):
    def test_01(self):
        class parserExample(grammar.Grammar):
            entry = "Example"
            grammar = """ 
            Example = [ id eof #setint(_, 12) 
                    ]
        
            """
        Ex = parserExample()
        res = Ex.parse("someExample")
        self.assertEqual(res.value, 12, "Can't set .value in the node to 12")
        class parserExample2(grammar.Grammar):
            entry = "Example"
            grammar = """ 
            Example = [ id eof #setstr(_, 'toto') 
                    ]
        
            """
        Ex = parserExample2()
        res = Ex.parse("someExample")
        self.assertEqual(res.value, 'toto', "Can't set .value in the node to 'toto'")
        class parserExample3(grammar.Grammar):
            entry = "Example"
            grammar = """ 
            Example = [ id:i eof #setcapture(_, i) 
                    ]
        
            """
        Ex = parserExample3()
        res = Ex.parse("someExample")
        self.assertEqual(res.value, 'someExample', "Can't set .value in the node to value of node 'i'")
