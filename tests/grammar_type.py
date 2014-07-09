import unittest
from pyrser.passes.to_yml import *
from pyrser.type_checking.fun import *
from pyrser.error import *
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
        res.type_node = Scope(
            sig=Fun('a', 'void', ['int']),
            is_namespace=False
        )
        res.type_node.add(Type("void"))
        res.type_node.add(Type("int"))
        res.infer_type(res.diagnostic)
        self.assertFalse(res.diagnostic.have_errors, "Bad inference")
        #print("RES FINAL: %s" %
        #    res.diagnostic.get_content(with_locinfos=True, with_details=True)
        #)
        # expr
        test = TL4T()
        res = test.parse("""
            var a = 42;
        """)
        txt = res.to_tl4t()
        self.assertEqual(str(txt), "var a = 42;\n")
        res.type_node = Scope(sig=Type('int'))
        res.infer_type(res.diagnostic)
        self.assertFalse(res.diagnostic.have_errors, "Bad inference")
        #print("RES FINAL: %s" %
        #    res.diagnostic.get_content(with_locinfos=True, with_details=True)
        #)
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
        #print(str(res.type_node))
        res.type_node.add(Type("void"))
        res.type_node.add(Type("string"))
        res.type_node.add(Type("int"))
        res.type_node.add(Var("a", "int"))
        # TODO: on veut aussi la liste de type reel des types variadiques
        res.infer_type(res.diagnostic)
        self.assertFalse(res.diagnostic.have_errors, "Bad inference")
        #print(
        #    res.diagnostic.get_content(with_locinfos=True, with_details=True)
        #)
        # Automatically add a translation
        test = TL4T()
        res = test.parse("""
            s = "toto" + 42;
        """)
        txt = str(res.to_tl4t())
        self.assertEqual(txt, 's = "toto" + 42;\n')
        res.type_node = Scope(is_namespace=False)
        res.type_node.add(Type("string"))
        res.type_node.add(Type("int"))
        res.type_node.add(Var("s", "string"))
        res.type_node.add(Fun("=", "string", ["string", "string"]))
        res.type_node.add(Fun("+", "string", ["string", "string"]))
        f = Fun("to_str", "string", ["int"])
        res.type_node.add(f)
        n = Notification(
            Severity.WARNING,
            "implicit conversion of int to string"
        )
        res.type_node.addTranslator(Translator(f, n))
        res.type_node.addTranslatorInjector(createFunWithTranslator)
        res.infer_type(res.diagnostic)
        self.assertFalse(res.diagnostic.have_errors, "Bad inference")
        #print(
        #    res.diagnostic.get_content(with_locinfos=True, with_details=True)
        #)
        self.assertEqual(str(res.to_tl4t()), 's = "toto" + to_str(42);\n', "Bad pretty print")

    def test_02_typerror(self):
        test = TL4T()
        res = test.parse("""
            a(42);
        """)
        res.type_node = Scope(sig=Fun('a', 'void', ['char']))
        res.infer_type(res.diagnostic)
        self.assertTrue(res.diagnostic.have_errors, "Bad error detection")
        # Automatically add a translation
        test = TL4T()
        res = test.parse("""
            s = "toto" + 42;
        """)
        txt = str(res.to_tl4t())
        self.assertEqual(txt, 's = "toto" + 42;\n')
        res.type_node = Scope(is_namespace=False)
        res.type_node.add(Type("string"))
        res.type_node.add(Type("int"))
        res.type_node.add(Var("s", "string"))
        res.type_node.add(Fun("=", "string", ["string", "string"]))
        res.type_node.add(Fun("+", "string", ["string", "string"]))
        f = Fun("to_str", "string", ["int"])
        res.type_node.add(f)
        n = Notification(
            Severity.ERROR,
            "implicit conversion of int to string"
        )
        res.type_node.addTranslator(Translator(f, n))
        res.type_node.addTranslatorInjector(createFunWithTranslator)
        res.infer_type(res.diagnostic)
        self.assertTrue(res.diagnostic.have_errors, "Bad inference")
        print(res.diagnostic.get_content(with_locinfos=True))
