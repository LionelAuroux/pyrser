import unittest
from tests.grammar.tl4t import *


class GrammarType_Test(unittest.TestCase):
    def test_01_typeliteral(self):
        test = TL4T()
        res = test.parse("""
            a(42);
        """)
        txt = res.to_tl4t()
        self.assertEqual(str(txt), "a(42);\n")
        res.type_node = Scope(sig=Signature('a', 'void', 'int'))
        res.infer_type()
        #test = TL4T()
        #res = test.parse("""
        #    a = 42;
        #""")
        #txt = res.to_tl4t()
        #self.assertEqual(str(txt), "a = 42;\n")
        #res.infer_type()
