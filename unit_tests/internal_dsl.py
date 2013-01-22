import unittest
from pyrser.dsl_parser import dsl_parser

class InternalDsl_Test(unittest.TestCase):
    def test_dslBase(self):
        """
            Basic test for dsl parsing
        """
        oRoot = dsl_parser.parse("""
            empty_clause ::= #num
            ;
        """, {}, "test1")
        print(repr(oRoot))
