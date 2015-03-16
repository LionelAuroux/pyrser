import unittest
from pyrser.passes.to_yml import *
from pyrser.type_system.fun import *
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
        # TODO: could be mask the attribute infer_node
        # and just provide a scope to infer_type method
        scope = Scope(
            sig=Fun('a', 'void', ['int']),
            is_namespace=False
        )
        scope.add(Type("void"))
        scope.add(Type("int"))
        res.infer_type(scope)
        print("!!![[%s]]" % res.to_yml())
        self.assertFalse(res.diagnostic.have_errors, "Bad inference")
        self.assertEqual(
            str(res.body[0].infer_node.scope_node.first().get_compute_sig()),
            "fun a : (int) -> void",
            "Bad computing of signature"
        )
        # expr
        test = TL4T()
        res = test.parse("""
            var a = 42;
        """)
        txt = res.to_tl4t()
        self.assertEqual(str(txt), "var a = 42;\n")
        scope = Scope(sig=Type('int'))
        res.infer_type(scope)
        self.assertFalse(res.diagnostic.have_errors, "Bad inference")
        #print(to_yml(res.body[0].type_node))
        #print(res.diagnostic)
        #print(res.body[0].type_node)
        # funcvariadic complex
        test = TL4T()
        res = test.parse("""
            printf("tutu %d", 42, a);
        """)
        txt = res.to_tl4t()
        self.assertEqual(str(txt), 'printf("tutu %d", 42, a);\n')
        scope = Scope(
            sig=Fun('printf', 'void', ['string'], variadic=True)
        )
        scope.add(Type("void"))
        scope.add(Type("string"))
        scope.add(Type("int"))
        scope.add(Var("a", "int"))
        # TODO: on veut aussi la liste de type reel des types variadiques
        res.infer_type(scope)
        self.assertFalse(res.diagnostic.have_errors, "Bad inference")
        self.assertEqual(
            str(res.body[0].type_node.first().get_compute_sig()),
            "fun printf : (string, int, int) -> void",
            "Bad computing of signature"
        )
        # funcvariadic simple
        test = TL4T()
        res = test.parse(r"""
            printf("cool\n");
        """)
        txt = res.to_tl4t()
        self.assertEqual(str(txt), 'printf("cool\\n");\n')
        scope = Scope(
            sig=Fun('printf', 'void', ['string'], variadic=True)
        )
        scope.add(Type("void"))
        scope.add(Type("string"))
        # TODO: on veut aussi la liste de type reel des types variadiques
        res.infer_type(scope)
        self.assertFalse(res.diagnostic.have_errors, "Bad inference")
        self.assertEqual(
            str(res.body[0].type_node.first().get_compute_sig()),
            "fun printf : (string) -> void",
            "Bad computing of signature"
        )
        # Automatically add a translation
        test = TL4T()
        res = test.parse("""
            s = "toto" + 42;
        """)
        txt = str(res.to_tl4t())
        self.assertEqual(txt, 's = "toto" + 42;\n')
        scope = Scope(is_namespace=False)
        scope.add(Type("string"))
        scope.add(Type("int"))
        scope.add(Var("s", "string"))
        scope.add(Fun("=", "string", ["string", "string"]))
        scope.add(Fun("+", "string", ["string", "string"]))
        f = Fun("to_str", "string", ["int"])
        scope.add(f)
        n = Notification(
            Severity.WARNING,
            "implicit conversion of int to string"
        )
        scope.addTranslator(Translator(f, n))
        scope.addTranslatorInjector(createFunWithTranslator)
        res.infer_type(scope)
        self.assertFalse(res.diagnostic.have_errors, "Bad inference")
        self.assertEqual(
            str(res.to_tl4t()),
            's = "toto" + to_str(42);\n',
            "Bad pretty print"
        )
        # poly-poly
        #test = TL4T()
        #res = test.parse("""
        #    f(a);
        #""")
        #txt = str(res.to_tl4t())
        #self.assertEqual(txt, 'f(a);\n')
        #res.type_node = Scope(is_namespace=False)
        #res.type_node.add(Type("?a"))
        #res.type_node.add(Var("a", "?a"))
        #res.type_node.add(Fun("f", "?", ["?"]))
        #res.infer_type(res.diagnostic)
        #print(res.diagnostic.get_content())
        #self.assertFalse(res.diagnostic.have_errors, "Bad inference")

    def test_02_typerror(self):
        test = TL4T()
        res = test.parse("""
            a(42);
        """)
        scope = Scope(sig=Fun('a', 'void', ['char']))
        res.infer_type(scope)
        self.assertTrue(res.diagnostic.have_errors, "Bad error detection")
        # Automatically add a translation
        test = TL4T()
        res = test.parse("""
            s = "toto" + 42;
        """)
        txt = str(res.to_tl4t())
        self.assertEqual(txt, 's = "toto" + 42;\n')
        scope = Scope(is_namespace=False)
        scope.add(Type("string"))
        scope.add(Type("int"))
        scope.add(Var("s", "string"))
        scope.add(Fun("=", "string", ["string", "string"]))
        scope.add(Fun("+", "string", ["string", "string"]))
        f = Fun("to_str", "string", ["int"])
        scope.add(f)
        n = Notification(
            Severity.ERROR,
            "implicit conversion of int to string"
        )
        scope.addTranslator(Translator(f, n))
        scope.addTranslatorInjector(createFunWithTranslator)
        res.infer_type(scope)
        self.assertTrue(res.diagnostic.have_errors, "Bad inference")
        self.assertEqual(res.diagnostic.get_infos()[Severity.ERROR], 1)
