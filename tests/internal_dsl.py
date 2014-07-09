import unittest
from pyrser import parsing
from pyrser import dsl
from pyrser import meta
from pyrser import error
import os


class InternalDsl_Test(unittest.TestCase):
    def test_01_one_rule(self):
        """
        Test default
        """
        bnf = dsl.EBNF("""
            the_rule = [ a ]
        """)
        res = bnf.get_rules()
        self.assertIn('the_rule', res)
        self.assertIsInstance(res['the_rule'], parsing.Rule)
        self.assertEqual(res['the_rule'].name, 'a')

    def test_02_two_rules(self):
        """
        Test default
        """
        bnf = dsl.EBNF("""
            the_rule=[a b c]
        """)
        res = bnf.get_rules()
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertIsInstance(res['the_rule'], parsing.Seq,
                              "failed in ParserTree type for node Seq")
        self.assertIsInstance(res['the_rule'][0], parsing.Rule,
                              "failed in ParserTree type for node Rule")
        self.assertTrue(res['the_rule'][0].name == "a",
                        "failed in name of rule 'a'")
        self.assertIsInstance(res['the_rule'][1], parsing.Rule,
                              "failed in ParserTree type for node Rule")
        self.assertTrue(res['the_rule'][1].name == "b",
                        "failed in name of rule 'b'")

    def test_03_more_rules(self):
        """
        Test default
        """
        bnf = dsl.EBNF("""
            the_rule = [ a b c]
        """)
        res = bnf.get_rules()
        self.assertTrue('the_rule' in res)
        self.assertIsInstance(res['the_rule'], parsing.Seq)
        self.assertIsInstance(res['the_rule'][0], parsing.Rule)
        self.assertTrue(res['the_rule'][0].name == "a")
        self.assertIsInstance(res['the_rule'][1], parsing.Rule)
        self.assertTrue(res['the_rule'][1].name == "b")
        self.assertIsInstance(res['the_rule'][2], parsing.Rule)
        self.assertTrue(res['the_rule'][2].name == "c")

    def test_04_one_alt(self):
        """
        Test default
        """
        bnf = dsl.EBNF("""
            the_rule = [ a | b ]
        """)
        res = bnf.get_rules()
        self.assertTrue('the_rule' in res)
        self.assertIsInstance(res['the_rule'], parsing.Alt)
        self.assertIsInstance(res['the_rule'][0], parsing.Rule)
        self.assertTrue(res['the_rule'][0].name == "a")
        self.assertIsInstance(res['the_rule'][1], parsing.Rule)
        self.assertTrue(res['the_rule'][1].name == "b")

    def test_05_two_alt(self):
        """
        Test default
        """
        bnf = dsl.EBNF("""
            the_rule = [ a | b | c ]
        """)
        res = bnf.get_rules()
        self.assertTrue('the_rule' in res)
        self.assertIsInstance(res['the_rule'], parsing.Alt)
        self.assertIsInstance(res['the_rule'][0], parsing.Rule)
        self.assertTrue(res['the_rule'][0].name == "a")
        self.assertIsInstance(res['the_rule'][1], parsing.Rule)
        self.assertTrue(res['the_rule'][1].name == "b")
        self.assertIsInstance(res['the_rule'][2], parsing.Rule)
        self.assertTrue(res['the_rule'][2].name == "c")

    def test_06_char(self):
        """
        Test default
        """
        bnf = dsl.EBNF("""
            the_rule = [ 'a' ]
        """)
        res = bnf.get_rules()
        self.assertTrue('the_rule' in res)
        self.assertIsInstance(res['the_rule'], parsing.Char)
        self.assertTrue(res['the_rule'].char == 'a')

    def test_07_string(self):
        """
        Test default
        """
        bnf = dsl.EBNF("""
            the_rule = [ "bonjour le monde" ]
        """)
        res = bnf.get_rules()
        self.assertTrue('the_rule' in res)
        self.assertIsInstance(res['the_rule'], parsing.Text)
        self.assertTrue(res['the_rule'].text == "bonjour le monde")

    def test_08_range(self):
        """
        Test default
        """
        bnf = dsl.EBNF("""
            the_rule = [ 'a'..'z' ]
        """)
        res = bnf.get_rules()
        self.assertTrue('the_rule' in res)
        self.assertIsInstance(res['the_rule'], parsing.Range)
        self.assertTrue(res['the_rule'].begin == 'a')
        self.assertTrue(res['the_rule'].end == 'z')

    def test_09_complexe(self):
        """
        Test default
        """
        bnf = dsl.EBNF("""
            the_rule = [ 'a'..'z' "tutu" 'a' | a b | z ]
        """)
        res = bnf.get_rules()
        self.assertTrue('the_rule' in res)
        self.assertIsInstance(res['the_rule'], parsing.Alt)
        self.assertIsInstance(res['the_rule'][0], parsing.Seq)
        self.assertIsInstance(res['the_rule'][0][0],
                              parsing.Range)
        self.assertTrue(res['the_rule'][0][0].begin == 'a')
        self.assertTrue(res['the_rule'][0][0].end == 'z')
        self.assertIsInstance(res['the_rule'][0][1],
                              parsing.Text)
        self.assertEqual(res['the_rule'][0][1].text, "tutu")
        self.assertIsInstance(res['the_rule'][0][2],
                              parsing.Char)
        self.assertTrue(res['the_rule'][0][2].char == 'a')
        self.assertIsInstance(res['the_rule'][1], parsing.Seq)
        self.assertIsInstance(res['the_rule'][1][0],
                              parsing.Rule)
        self.assertTrue(res['the_rule'][1][0].name == "a")
        self.assertTrue(res['the_rule'][1][1].name == "b")
        self.assertIsInstance(res['the_rule'][2], parsing.Rule)
        self.assertTrue(res['the_rule'][2].name == "z")

    def test_10_repoption(self):
        """
        Test default
        """
        bnf = dsl.EBNF("""
            the_rule = [ a? ]
        """)
        res = bnf.get_rules()
        self.assertTrue('the_rule' in res)
        self.assertIsInstance(res['the_rule'], parsing.RepOptional)
        self.assertTrue(res['the_rule'].pt.name == 'a')

    def test_11_rep0N(self):
        """
        Test default
        """
        bnf = dsl.EBNF("""
            the_rule = [ a* ]
        """)
        res = bnf.get_rules()
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertIsInstance(res['the_rule'], parsing.Rep0N)
        self.assertIsInstance(res['the_rule'].pt, parsing.Rule)
        self.assertTrue(res['the_rule'].pt.name == 'a')

    def test_12_rep1N(self):
        """
        Test default
        """
        bnf = dsl.EBNF("""
            the_rule = [ [a "toto"]+ ]
        """)
        res = bnf.get_rules()
        self.assertTrue('the_rule' in res)
        self.assertIsInstance(res['the_rule'], parsing.Rep1N)
        self.assertTrue(res['the_rule'].pt[0].name == 'a')
        self.assertTrue(res['the_rule'].pt[1].text == "toto")

    def test_13_complementedRepeatedRule(self):
        bnf = dsl.EBNF("""
            the_rule = [ ~a+ ]
        """)
        res = bnf.get_rules()
        self.assertTrue('the_rule' in res)
        self.assertIsInstance(res['the_rule'], parsing.Rep1N)
        self.assertIsInstance(res['the_rule'].pt, parsing.Complement)
        self.assertEqual(res['the_rule'].pt.pt.name, 'a')

    def test_14_negatedRule(self):
        bnf = dsl.EBNF("""
            the_rule = [ !a ]
        """)
        res = bnf.get_rules()
        self.assertTrue('the_rule' in res)
        self.assertIsInstance(res['the_rule'], parsing.Neg)
        self.assertEqual(res['the_rule'].pt.name, 'a')

    def test_15_negatedRepeatedRule(self):
        bnf = dsl.EBNF("""
            the_rule = [ !a+ ]
        """)
        with self.assertRaises(error.Diagnostic) as pe:
            r = bnf.get_rules()
        self.assertEqual(
            pe.exception.logs[0].msg,
            "Cannot repeat a negated rule",
            "Bad message"
        )

    def test_16_lookaheadRule(self):
        bnf = dsl.EBNF("""
            the_rule = [ !!a ]
        """)
        res = bnf.get_rules()
        self.assertTrue('the_rule' in res)
        self.assertIsInstance(res['the_rule'], parsing.LookAhead)
        self.assertEqual(res['the_rule'].pt.name, 'a')

    def test_17_lookaheadRepeatedRule(self):
        bnf = dsl.EBNF("""
            the_rule = [ !!a+ ]
        """)
        with self.assertRaises(error.Diagnostic) as pe:
            r = bnf.get_rules()
        self.assertEqual(
            pe.exception.logs[0].msg,
            "Cannot repeat a lookahead rule",
            "Bad message"
        )

    def test_18_hookNoParam(self):
        bnf = dsl.EBNF("""
            the_rule = [ #hook ]
        """)
        res = bnf.get_rules()
        self.assertTrue('the_rule' in res)
        self.assertIsInstance(res['the_rule'], parsing.Hook)

    def test_19_hookOneParamStr(self):
        @meta.hook(parsing.Parser)
        def my_hook_txt(self, txt):
            self.test.assertEqual(txt, "cool",
                                  'failed to receive "cool" in hook')
            self.test.assertTrue(txt == "cool")
            return True

        bnf = dsl.EBNF("""
            the_rule = [ #my_hook_txt("cool") ]
        """)
        res = bnf.get_rules()
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertIsInstance(res['the_rule'], parsing.Hook)
        self.assertTrue(res['the_rule'].name == "my_hook_txt")
        dummyData = parsing.Parser()
        dummyData.set_rules(res)
        dummyData.test = self
        #with dummyData as s:
        res = dummyData.eval_rule('the_rule')
        self.assertTrue(res)

    def test_20_hookOneParamChar(self):
        @meta.hook(parsing.Parser)
        def my_hook_char(self, txt):
            self.test.assertEqual(txt, "\t", 'failed to receive "\t" in hook')
            return True

        bnf = dsl.EBNF("""
            the_rule = [ #my_hook_char('\t') ]
        """)
        res = bnf.get_rules()
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertIsInstance(res['the_rule'], parsing.Hook)
        self.assertTrue(res['the_rule'].name == "my_hook_char")
        dummyData = parsing.Parser()
        dummyData.set_rules(res)
        dummyData.test = self
        #with dummyData as s:
        res = dummyData.eval_rule('the_rule')
        self.assertTrue(res)

    def test_21_hookOneParamNum(self):
        @meta.hook(parsing.Parser)
        def my_hook_num(self, num):
            self.test.assertEqual(num, 123456,
                                  'failed to receive 123456 in hook')
            self.test.assertTrue(num == 123456)
            return True

        bnf = dsl.EBNF("""
            the_rule = [ #my_hook_num(123456) ]
        """)
        res = bnf.get_rules()
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertIsInstance(res['the_rule'], parsing.Hook)
        self.assertTrue(res['the_rule'].name == "my_hook_num")
        dummyData = parsing.Parser()
        dummyData.set_rules(res)
        dummyData.test = self
        #with dummyData as s:
        res = dummyData.eval_rule('the_rule')
        self.assertTrue(res)

    def test_22_hookOneParamId(self):
        @meta.hook(parsing.Parser)
        def my_hook_id(self, n):
            self.test.assertIsInstance(n, parsing.Node)
            return True

        bnf = dsl.EBNF("""
            the_rule = [ #my_hook_id(_) ]
        """)
        res = bnf.get_rules()
        self.assertTrue('the_rule' in res)
        self.assertIsInstance(res['the_rule'], parsing.Hook)
        self.assertTrue(res['the_rule'].name == "my_hook_id")
        dummyData = parsing.Parser()
        dummyData.set_rules(res)
        dummyData.test = self
        #with dummyData as s:
        res = dummyData.eval_rule('the_rule')
        self.assertTrue(res)

    def test_23_hookParams(self):
        @meta.hook(parsing.Parser)
        def my_hook_params(self, n, num, txt):
            self.test.assertIsInstance(n, parsing.Node)
            self.test.assertTrue(num == 123456)
            self.test.assertTrue(txt == "cool")
            return True

        bnf = dsl.EBNF("""
            the_rule = [ #my_hook_params(_, 123456, "cool") ]
        """)
        res = bnf.get_rules()
        self.assertTrue('the_rule' in res)
        self.assertIsInstance(res['the_rule'], parsing.Hook)
        self.assertTrue(res['the_rule'].name == "my_hook_params")
        dummyData = parsing.Parser()
        dummyData.set_rules(res)
        dummyData.test = self
        #with dummyData as s:
        res = dummyData.eval_rule('the_rule')
        self.assertTrue(res)

    def test_24_hookAndCapture(self):
        @meta.hook(parsing.Parser)
        def my_hook_multi(self, n1, n2, n3):
            self.test.assertTrue(self.value(n1) == "456")
            self.test.assertTrue(self.value(n2) == '"toto"')
            self.test.assertTrue(self.value(n3) == "blabla")
            return True

        bnf = dsl.EBNF("""

            N = [ Base.num ]

            S = [ Base.string ]

            I = [ Base.id ]

            the_rule = [ N:nth S:t I:i
                         #my_hook_multi(nth, t, i)
            ]
        """)
        res = bnf.get_rules()
        self.assertTrue('the_rule' in res)
        self.assertIsInstance(res['the_rule'], parsing.Seq)
        self.assertTrue(res['the_rule'][-1].name == "my_hook_multi")
        dummyData = parsing.Parser("""
            456    "toto"        blabla
            """)
        dummyData.set_rules(res)
        dummyData.test = self
        #with dummyData as s:
        eval_res = dummyData.eval_rule('the_rule')
        self.assertTrue(eval_res)

    def test_25_directive(self):
        class dummyDir(parsing.DirectiveWrapper):
            def begin(self, parser, a: int, b: int, c: int):
                parser.test.assertTrue(a == 1)
                parser.test.assertTrue(b == 2)
                parser.test.assertTrue(c == 3)
                # for workflow checking
                parser.workflow = 1
                return True

            def end(self, parser, a: int, b: int, c: int):
                parser.test.assertTrue(a == 1)
                parser.test.assertTrue(b == 2)
                parser.test.assertTrue(c == 3)
                # for workflow checking
                parser.test.assertTrue(parser.workflow == 2)
                return True

        @meta.hook(parsing.Parser)
        def my_hook(self):
            # for workflow checking
            self.test.assertTrue(self.workflow == 1)
            self.workflow = 2
            return True

        dsl.EBNF.set_directives({'toto.dummyDir': dummyDir})
        bnf = dsl.EBNF("""
            the_rule = [ @toto.dummyDir(1, 2, 3) test ]

            test = [ #my_hook Base.eof ]
        """)
        res = bnf.get_rules()
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        dummyData = parsing.Parser()
        dummyData.set_rules(res)
        dummyData.test = self
        #with dummyData as s:
        res = dummyData.eval_rule('the_rule')
        self.assertTrue(res)

    def test_25_list_id(self):
        @meta.hook(parsing.Parser)
        def in_list(self, ls, ident):
            if not hasattr(ls, 'list'):
                ls.list = []
            ls.list.append(self.value(ident))
            return True

        bnf = dsl.EBNF("""

            I = [ id ]

            list = [ [I : i #in_list(_, i) ]+ ]
        """)
        res = bnf.get_rules()
        self.assertTrue('list' in res)
        dummyData = parsing.Parser("""
            a     b c   d        e   f
        """)
        dummyData.set_rules(res)
        dummyData.test = self
        #with dummyData as s:
        eval_res = dummyData.eval_rule('list')
        self.assertTrue(eval_res)
        self.assertTrue(eval_res.list[0] == "a")
        self.assertTrue(eval_res.list[1] == "b")
        self.assertTrue(eval_res.list[2] == "c")
        self.assertTrue(eval_res.list[3] == "d")
        self.assertTrue(eval_res.list[4] == "e")
        self.assertTrue(eval_res.list[5] == "f")

    def test_26_set(self):
        class dummyList(parsing.Node):
            def __init__(self):
                self._ls = []

            def append(self, x):
                self._ls.append(x)

            def __getitem__(self, n):
                return self._ls[n]

        @meta.hook(parsing.Parser)
        def in_list(self, ls, ident):
            if type(ls) is parsing.Node:
                ls.set(dummyList())
            ls.append(self.value(ident))
            return True

        bnf = dsl.EBNF("""

            I = [ id ]

            list = [ [I : i #in_list(_, i) ]+ ]
        """)
        res = bnf.get_rules()
        self.assertTrue('list' in res)
        self.assertTrue('I' in res)
        dummyData = parsing.Parser("""
            a     b c   d        e   f
        """)
        dummyData.set_rules(res)
        dummyData.test = self
        #with dummyData as s:
        eval_res = dummyData.eval_rule('list')
        self.assertTrue(eval_res)
        self.assertTrue(eval_res[0] == "a")
        self.assertTrue(eval_res[1] == "b")
        self.assertTrue(eval_res[2] == "c")
        self.assertTrue(eval_res[3] == "d")
        self.assertTrue(eval_res[4] == "e")
        self.assertTrue(eval_res[5] == "f")

    def test_27_nodescope(self):
        @meta.hook(parsing.Parser)
        def put(self, ast):
            # A.put visible in subrules
            ast.put = True
            return True

        @meta.hook(parsing.Parser)
        def check1(self):
            self.test.assertTrue('A' in self.rule_nodes)
            # _ is from rule1, not main
            self.test.assertFalse(hasattr(self.rule_nodes['_'], 'put'))
            # return of rule1 with .toto == True
            self.rule_nodes['_'].toto = True
            return True

        @meta.hook(parsing.Parser)
        def check2(self):
            self.test.assertTrue('A' in self.rule_nodes)
            self.test.assertTrue('B' in self.rule_nodes)
            return False

        @meta.hook(parsing.Parser)
        def check3(self):
            self.test.assertTrue('A' in self.rule_nodes)
            # B no more living (alternative)
            self.test.assertFalse('B' in self.rule_nodes)
            return True

        @meta.hook(parsing.Parser)
        def toto(self):
            self.test.assertTrue(hasattr(self.rule_nodes['r'], 'toto'))
            self.test.assertTrue(hasattr(self.rule_nodes['r'], 'bla'))
            return True

        @meta.hook(parsing.Parser)
        def check4(self):
            self.rule_nodes['_'].bla = True
            return True

        bnf = dsl.EBNF("""
            main =
            [ __scope__:A #put(_)
                rule1:r #toto eof
            ]

            rule1 =
            [
                #check1 __scope__:B #check2
                | #check3 #check4
            ]
        """)
        res = bnf.get_rules()
        self.assertTrue('main' in res)
        self.assertTrue('rule1' in res)
        dummyData = parsing.Parser("")
        dummyData.set_rules(res)
        dummyData.test = self
        #with dummyData as s:
        eval_res = dummyData.eval_rule('main')
