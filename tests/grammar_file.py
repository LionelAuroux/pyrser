import unittest
import os
from pyrser import grammar, meta
from pyrser import error
from pyrser.passes.to_yml import *
from pyrser.hooks.echo import *
from tests.grammar.tl4t import *


class GrammarFile_Test(unittest.TestCase):
    def test_01_dynparse(self):
        txtbnf = grammar.from_string("""
            plop =[ id:i #test_hook(_, i)]
        """)

        @meta.hook(txtbnf)
        def test_hook(self, l, i):
            self.test.assertEqual(self.value(i), "cool")
            l.node = self.value(i)
            return True
        itxt = txtbnf()
        itxt.test = self
        res = itxt.parse("cool", "plop")
        self.assertEqual(res.node, "cool")

    def test_02_json(self):
        """
        Test JSON
        """
        JSON = grammar.from_file(os.getcwd() + "/tests/bnf/json.bnf", 'json')

        # add hook to the dynamically created base class
        @meta.hook(JSON)
        def is_num(self, ast, n):
            ast.node = float(self.value(n))
            return True

        @meta.hook(JSON)
        def is_str(self, ast, s):
            ast.node = self.value(s).strip('"')
            return True

        @meta.hook(JSON)
        def is_bool(self, ast, b):
            bval = self.value(b)
            if bval == "true":
                ast.node = True
            if bval == "false":
                ast.node = False
            return True

        @meta.hook(JSON)
        def is_none(self, ast):
            ast.node = None
            return True

        @meta.hook(JSON)
        def is_pair(self, ast, s, v):
            ast.node = (self.value(s).strip('"'), v.node)
            return True

        @meta.hook(JSON)
        def is_array(self, ast):
            ast.node = []
            return True

        @meta.hook(JSON)
        def add_item(self, ast, item):
            ast.node.append(item.node)
            return True

        @meta.hook(JSON)
        def is_dict(self, ast):
            ast.node = {}
            return True

        @meta.hook(JSON)
        def add_kv(self, ast, item):
            ast.node[item.node[0]] = item.node[1]
            return True

        json = JSON()
        res = json.parse('{"test":12}')
        self.assertEqual(res.node['test'], 12)
        res = json.parse('{"test":12,"puf":[1,2,3]}')
        self.assertEqual(res.node['puf'][1], 2)
        res = json.parse('{"test":12,"puf":[1,2,3],"obj":{"flags":true}}')
        self.assertTrue(res.node['obj']['flags'])

    def test_03_tl4t_parse(self):
        """
        Test TL4T
        """
        test = TL4T()
        res = test.parse("""
            var a : int;
        """)
        self.assertTrue(res)
        self.assertTrue(isinstance(res.body[0], DeclVar))
        txt = res.to_tl4t()
        self.assertEqual(str(txt), "var a : int;\n")
        res = test.parse("""
            fun a() : int;
        """)
        self.assertTrue(res)
        self.assertTrue(isinstance(res.body[0], DeclFun))
        self.assertTrue(res.body[0].t == 'int')
        txt = res.to_tl4t()
        self.assertEqual(str(txt), "fun a() : int;\n")
        res = test.parse("""
            fun a(x : str) : int;
        """)
        self.assertTrue(res)
        self.assertTrue(isinstance(res.body[0], DeclFun))
        self.assertTrue(isinstance(res.body[0].p[0], Param))
        self.assertTrue(res.body[0].p[0].name, "x")
        self.assertTrue(res.body[0].p[0].t, "int")
        txt = res.to_tl4t()
        self.assertEqual(str(txt), "fun a(x : str) : int;\n")
        res = test.parse("""
            fun a(x : str, y : int) : int;
        """)
        self.assertTrue(res)
        self.assertTrue(isinstance(res.body[0], DeclFun))
        self.assertTrue(isinstance(res.body[0].p[0], Param))
        self.assertTrue(res.body[0].p[0].name, "x")
        self.assertTrue(res.body[0].p[0].t, "int")
        txt = res.to_tl4t()
        self.assertEqual(str(txt), "fun a(x : str, y : int) : int;\n")
        res = test.parse("""
            fun a(x : str) : int
            {
                var z : toto;
            }
        """)
        self.assertTrue(res)
        self.assertTrue(isinstance(res.body[0], DeclFun))
        self.assertTrue(isinstance(res.body[0].p[0], Param))
        self.assertTrue(res.body[0].p[0].name, "x")
        self.assertTrue(res.body[0].p[0].t, "int")
        self.assertTrue(isinstance(res.body[0].block.body[0], DeclVar))
        self.assertTrue(res.body[0].block.body[0].name, "z")
        self.assertTrue(res.body[0].block.body[0].t, "toto")
        txt = res.to_tl4t()
        self.assertEqual(
            str(txt),
            "fun a(x : str) : int\n{\n    var z : toto;\n}"
        )
        res = test.parse("""
            a = 42;
        """)
        self.assertTrue(res)
        self.assertTrue(isinstance(res.body[0], ExprStmt))
        txt = res.to_tl4t()
        self.assertEqual(str(txt), "a = 42;\n")
        res = test.parse("""
            a = +--+42;
        """)
        self.assertTrue(res)
        self.assertTrue(isinstance(res.body[0], ExprStmt))
        txt = res.to_tl4t()
        self.assertEqual(str(txt), "a = +--+42;\n")
        res = test.parse("""
            a = 12 - 42;
        """)
        self.assertTrue(res)
        self.assertTrue(isinstance(res.body[0], ExprStmt))
        txt = res.to_tl4t()
        self.assertEqual(str(txt), "a = 12 - 42;\n")
        res = test.parse("""
            a = f(12, "blabla", z);
        """)
        self.assertTrue(res)
        self.assertTrue(isinstance(res.body[0], ExprStmt))
        txt = res.to_tl4t()
        self.assertEqual(str(txt), """a = f(12, "blabla", z);\n""")
        res = test.parse("""
            a = (7 - 8) * 43;
        """)
        self.assertTrue(res)
        self.assertTrue(isinstance(res.body[0], ExprStmt))
        txt = res.to_tl4t()
        self.assertEqual(str(txt), """a = (7 - 8) * 43;\n""")
        res = test.parse("""
            a = (7 - 8) * 43 - 5;
        """, "expr")
        self.assertTrue(res)
        res = test.parse("""
            a = 1 < 2 || 3;
        """, "expr")
        self.assertTrue(res)
        res = test.parse("""
            a = 1 < 2 << 3;
        """, "expr")
        self.assertTrue(res)

    def test_04_file_error(self):
        """
        Test ERROR
        """
        with self.assertRaises(error.Diagnostic) as pe:
            T = grammar.from_file(
                os.getcwd() + "/tests/bnf/error_bracket.bnf",
                'source'
            )
        self.assertTrue(pe.exception, "Can't detect error in BNF")
        self.assertEqual(
            pe.exception.logs[0].msg,
            "Expected ']'",
            "Bad message in Error"
        )
        self.assertEqual(pe.exception.logs[0].location.line, 2, "Bad line")
        self.assertEqual(pe.exception.logs[0].location.col, 7, "Bad col")
        with self.assertRaises(error.Diagnostic) as pe:
            T = grammar.from_file(
                os.getcwd() + "/tests/bnf/error_bracket2.bnf",
                'source'
            )
        self.assertTrue(pe.exception, "Can't detect error in BNF")
        self.assertEqual(
            pe.exception.logs[0].msg,
            "Expected '['",
            "Bad message in Error"
        )
        self.assertEqual(pe.exception.logs[0].location.line, 2, "Bad line")
        self.assertEqual(pe.exception.logs[0].location.col, 1, "Bad col")
        with self.assertRaises(error.Diagnostic) as pe:
            T = grammar.from_file(
                os.getcwd() + "/tests/bnf/error_rule.bnf",
                'source'
            )
        self.assertTrue(pe.exception, "Can't detect error in BNF")
        self.assertEqual(
            pe.exception.logs[0].msg,
            "Expected '='",
            "Bad message in Error"
        )
        self.assertEqual(pe.exception.logs[0].location.line, 2, "Bad line")
        self.assertEqual(pe.exception.logs[0].location.col, 1, "Bad col")
        with self.assertRaises(error.Diagnostic) as pe:
            T = grammar.from_file(
                os.getcwd() + "/tests/bnf/error_bracket3.bnf",
                'source'
            )
        self.assertTrue(pe.exception, "Can't detect error in BNF")
        self.assertEqual(
            pe.exception.logs[0].msg,
            "Expected sequences",
            "Bad message in Error"
        )
        self.assertEqual(pe.exception.logs[0].location.line, 1, "Bad line")
        self.assertEqual(pe.exception.logs[0].location.col, 8, "Bad col")
        with self.assertRaises(error.Diagnostic) as pe:
            T = grammar.from_file(
                os.getcwd() + "/tests/bnf/error_empty.bnf",
                'source'
            )
        self.assertTrue(pe.exception, "Can't detect error in BNF")
        self.assertEqual(
            pe.exception.logs[0].msg,
            "Parse error in 'directive' in EBNF bnf",
            "Bad message in Error"
        )
        self.assertEqual(pe.exception.logs[0].location.line, 1, "Bad line")
        self.assertEqual(pe.exception.logs[0].location.col, 7, "Bad col")
