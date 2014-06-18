import unittest
from pyrser.passes.to_yml import *
from pyrser.type_checking.fun import *
from tests.grammar.tl4t import *


class GrammarType_Test(unittest.TestCase):
    def test_01_typeliteral(self):
        # fun call
        test = TL4T()
        res = test.parse("""
            a(42);
        """)
        txt = res.to_tl4t()
        self.assertEqual(str(txt), "a(42);\n")
        res.type_node = Scope(sig=Fun('a', 'void', ['int']))
        res.type_node.add(Type("void"))
        res.type_node.add(Type("int"))
        res.infer_type()
        # expr
        test = TL4T()
        res = test.parse("""
            a = 42;
        """)
        txt = res.to_tl4t()
        self.assertEqual(str(txt), "a = 42;\n")
        res.type_node = Scope(sig=Type('int'))
        res.infer_type()
        # funcvariadic
        test = TL4T()
        res = test.parse("""
            printf("tutu %d", 42, a);
        """)
        txt = res.to_tl4t()
        self.assertEqual(str(txt), 'printf("tutu %d", 42, a);\n')
        res.type_node = Scope(
            sig=Fun('printf', 'void', ['string'], variadic=True)
        )
        res.type_node.add(Type("void"))
        res.type_node.add(Type("string"))
        res.type_node.add(Type("int"))
        res.type_node.add(Var("a", "int"))
        res.infer_type()
        print(to_yml(res))
