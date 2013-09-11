import unittest

from pyrser import grammar, meta


class GrammarFile_Test(unittest.TestCase):
    def test_01_dynparse(self):
        txtbnf = grammar.from_string("""
            plop ::= id:i #test_hook(_, i)
            ;
        """)
        @meta.hook(txtbnf)
        def test_hook(self, l, i):
            self.test.assertEqual(i.value, "cool")
            l.node = i.value
            return True
        itxt = txtbnf()
        itxt.test = self
        res = itxt.parse("cool", "plop")
        self.assertEqual(res.node, "cool")

    def test_02_json(self):
        """
        Test JSON
        """
        import os
        JSON = grammar.from_file(os.getcwd() + "/tests/bnf/json.bnf")
        # add hook to the dynamically created base class
        @meta.hook(JSON)
        def is_num(self, ast, n):
            ast.node = float(n.value)
            return True
        @meta.hook(JSON)
        def is_str(self, ast, s):
            ast.node = s.value.strip('"')
            return True
        @meta.hook(JSON)
        def is_bool(self, ast, b):
            if b.value == "true":
                ast.node = True
            if b.value == "false":
                ast.node = False
            return True
        @meta.hook(JSON)
        def is_none(self, ast):
            ast.node = None
            return True
        @meta.hook(JSON)
        def is_pair(self, ast, s, v):
            ast.node = (s.value.strip('"'), v.node)
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
        res = json.parse('{"test":12}', "json")
        self.assertEqual(res.node['test'], 12)
        res = json.parse('{"test":12,"puf":[1,2,3]}', "json")
        self.assertEqual(res.node['puf'][1], 2)
        res = json.parse('{"test":12,"puf":[1,2,3],"obj":{"flags":true}}', "json")
        self.assertTrue(res.node['obj']['flags'])
