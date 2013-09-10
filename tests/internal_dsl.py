import unittest

from pyrser import parsing
from pyrser import dsl
from pyrser import meta
from pyrser import error


class InternalDsl_Test(unittest.TestCase):
    def test_01_one_rule(self):
        """
        Test default
        """
        bnf = dsl.EBNF("""
            the_rule ::= a
            ;
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
            the_rule::=a b c
            ;
        """)
        res = bnf.get_rules()
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertIsInstance(res['the_rule'], parsing.Seq,
                              "failed in ParserTree type for node Seq")
        self.assertIsInstance(res['the_rule'].ptlist[0], parsing.Rule,
                              "failed in ParserTree type for node Rule")
        self.assertTrue(res['the_rule'].ptlist[0].name == "a",
                        "failed in name of rule 'a'")
        self.assertIsInstance(res['the_rule'].ptlist[1], parsing.Rule,
                              "failed in ParserTree type for node Rule")
        self.assertTrue(res['the_rule'].ptlist[1].name == "b",
                        "failed in name of rule 'b'")
        self.assertIsInstance(res['the_rule'], parsing.Seq)
        self.assertIsInstance(res['the_rule'].ptlist[0], parsing.Rule)
        self.assertTrue(res['the_rule'].ptlist[0].name == "a")
        self.assertIsInstance(res['the_rule'].ptlist[1], parsing.Rule)
        self.assertTrue(res['the_rule'].ptlist[1].name == "b")

    def test_03_more_rules(self):
        """
        Test default
        """
        bnf = dsl.EBNF("""
            the_rule ::= a b c
            ;
        """)
        res = bnf.get_rules()
        self.assertTrue('the_rule' in res)
        self.assertIsInstance(res['the_rule'], parsing.Seq)
        self.assertIsInstance(res['the_rule'].ptlist[0], parsing.Rule)
        self.assertTrue(res['the_rule'].ptlist[0].name == "a")
        self.assertIsInstance(res['the_rule'].ptlist[1], parsing.Rule)
        self.assertTrue(res['the_rule'].ptlist[1].name == "b")
        self.assertIsInstance(res['the_rule'].ptlist[2], parsing.Rule)
        self.assertTrue(res['the_rule'].ptlist[2].name == "c")

    def test_04_one_alt(self):
        """
        Test default
        """
        bnf = dsl.EBNF("""
            the_rule ::= a | b
            ;
        """)
        res = bnf.get_rules()
        self.assertTrue('the_rule' in res)
        self.assertIsInstance(res['the_rule'], parsing.Alt)
        self.assertIsInstance(res['the_rule'].ptlist[0], parsing.Rule)
        self.assertTrue(res['the_rule'].ptlist[0].name == "a")
        self.assertIsInstance(res['the_rule'].ptlist[1], parsing.Rule)
        self.assertTrue(res['the_rule'].ptlist[1].name == "b")

    def test_05_two_alt(self):
        """
        Test default
        """
        bnf = dsl.EBNF("""
            the_rule ::= a | b | c
            ;
        """)
        res = bnf.get_rules()
        self.assertTrue('the_rule' in res)
        self.assertIsInstance(res['the_rule'], parsing.Alt)
        self.assertIsInstance(res['the_rule'].ptlist[0], parsing.Rule)
        self.assertTrue(res['the_rule'].ptlist[0].name == "a")
        self.assertIsInstance(res['the_rule'].ptlist[1], parsing.Rule)
        self.assertTrue(res['the_rule'].ptlist[1].name == "b")
        self.assertIsInstance(res['the_rule'].ptlist[2], parsing.Rule)
        self.assertTrue(res['the_rule'].ptlist[2].name == "c")

    def test_06_char(self):
        """
        Test default
        """
        bnf = dsl.EBNF("""
            the_rule ::= 'a'
            ;
        """)
        res = bnf.get_rules()
        self.assertTrue('the_rule' in res)
        self.assertIsInstance(res['the_rule'], parsing.Call)
        self.assertIs(res['the_rule'].callObject, parsing.Parser.read_char)
        self.assertTrue(res['the_rule'].params[0] == 'a')

    def test_07_string(self):
        """
        Test default
        """
        bnf = dsl.EBNF("""
            the_rule ::= "bonjour le monde"
            ;
        """)
        res = bnf.get_rules()
        self.assertTrue('the_rule' in res)
        self.assertIsInstance(res['the_rule'], parsing.Call)
        self.assertIs(res['the_rule'].callObject, parsing.Parser.read_text)
        self.assertTrue(res['the_rule'].params[0] == "bonjour le monde")

    def test_08_range(self):
        """
        Test default
        """
        bnf = dsl.EBNF("""
            the_rule ::= 'a'..'z'
            ;
        """)
        res = bnf.get_rules()
        self.assertTrue('the_rule' in res)
        self.assertIsInstance(res['the_rule'], parsing.Call)
        self.assertIs(res['the_rule'].callObject, parsing.Parser.read_range)
        self.assertTrue(res['the_rule'].params[0] == 'a')
        self.assertTrue(res['the_rule'].params[1] == 'z')

    def test_09_complexe(self):
        """
        Test default
        """
        bnf = dsl.EBNF("""
            the_rule ::= 'a'..'z' "tutu" 'a' | a b | z
            ;
        """)
        res = bnf.get_rules()
        self.assertTrue('the_rule' in res)
        self.assertIsInstance(res['the_rule'], parsing.Alt)
        self.assertIsInstance(res['the_rule'].ptlist[0], parsing.Seq)
        self.assertIsInstance(res['the_rule'].ptlist[0].ptlist[0],
                              parsing.Call)
        self.assertIs(res['the_rule'].ptlist[0].ptlist[0].callObject,
                      parsing.Parser.read_range)
        self.assertTrue(res['the_rule'].ptlist[0].ptlist[0].params[0] == 'a')
        self.assertTrue(res['the_rule'].ptlist[0].ptlist[0].params[1] == 'z')
        self.assertIsInstance(res['the_rule'].ptlist[0].ptlist[1],
                              parsing.Call)
        self.assertIs(res['the_rule'].ptlist[0].ptlist[1].callObject,
                      parsing.Parser.read_text)
        self.assertEqual(res['the_rule'].ptlist[0].ptlist[1].params[0], "tutu")
        self.assertIsInstance(res['the_rule'].ptlist[0].ptlist[2],
                              parsing.Call)
        self.assertIs(res['the_rule'].ptlist[0].ptlist[2].callObject,
                      parsing.Parser.read_char)
        self.assertIsInstance(res['the_rule'].ptlist[1], parsing.Seq)
        self.assertIsInstance(res['the_rule'].ptlist[1].ptlist[0],
                              parsing.Rule)
        self.assertTrue(res['the_rule'].ptlist[1].ptlist[0].name == "a")
        self.assertTrue(res['the_rule'].ptlist[1].ptlist[1].name == "b")
        self.assertIsInstance(res['the_rule'].ptlist[2], parsing.Rule)
        self.assertTrue(res['the_rule'].ptlist[2].name == "z")

    def test_10_repoption(self):
        """
        Test default
        """
        bnf = dsl.EBNF("""
            the_rule ::= a?
            ;
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
            the_rule ::= [a]*
            ;
        """)
        res = bnf.get_rules()
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertIsInstance(res['the_rule'], parsing.Rep0N)
        self.assertTrue(res['the_rule'].pt.name == 'a')

    def test_12_rep1N(self):
        """
        Test default
        """
        bnf = dsl.EBNF("""
            the_rule ::= [a "toto"]+
            ;
        """)
        res = bnf.get_rules()
        self.assertTrue('the_rule' in res)
        self.assertIsInstance(res['the_rule'], parsing.Rep1N)
        self.assertTrue(res['the_rule'].pt.ptlist[0].name == 'a')
        self.assertTrue(res['the_rule'].pt.ptlist[1].params[0] == "toto")

    def test_13_complementedRepeatedRule(self):
        bnf = dsl.EBNF("""
            the_rule ::= ~a+
            ;
        """)
        res = bnf.get_rules()
        self.assertTrue('the_rule' in res)
        self.assertIsInstance(res['the_rule'], parsing.Rep1N)
        self.assertIsInstance(res['the_rule'].pt, parsing.Complement)
        self.assertEqual(res['the_rule'].pt.pt.name, 'a')

    def test_14_negatedRule(self):
        bnf = dsl.EBNF("""
            the_rule ::= !a
            ;
        """)
        res = bnf.get_rules()
        self.assertTrue('the_rule' in res)
        self.assertIsInstance(res['the_rule'], parsing.Neg)
        self.assertEqual(res['the_rule'].pt.name, 'a')

    def test_15_negatedRepeatedRule(self):
        bnf = dsl.EBNF("""
            the_rule ::= !a+
            ;
        """)
        with self.assertRaises(error.ParseError):
            bnf.get_rules()

    def test_16_lookaheadRule(self):
        bnf = dsl.EBNF("""
            the_rule ::= !!a
            ;
        """)
        res = bnf.get_rules()
        self.assertTrue('the_rule' in res)
        self.assertIsInstance(res['the_rule'], parsing.LookAhead)
        self.assertEqual(res['the_rule'].pt.name, 'a')

    def test_17_negatedRepeatedRule(self):
        bnf = dsl.EBNF("""
            the_rule ::= !!a+
            ;
        """)
        with self.assertRaises(error.ParseError):
            bnf.get_rules()

    def test_18_hookNoParam(self):
        bnf = dsl.EBNF("""
            the_rule ::= #hook
            ;
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
            the_rule ::= #my_hook_txt("cool")
            ;
        """)
        res = bnf.get_rules()
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertIsInstance(res['the_rule'], parsing.Hook)
        self.assertTrue(res['the_rule'].name == "my_hook_txt")
        dummyData = parsing.Parser()
        dummyData.set_rules(res)
        dummyData.test = self
        self.assertTrue(dummyData.eval_rule('the_rule'))

    def test_20_hookOneParamChar(self):
        @meta.hook(parsing.Parser)
        def my_hook_char(self, txt):
            self.test.assertEqual(txt, "\t", 'failed to receive "\t" in hook')
            return True
        bnf = dsl.EBNF("""
            the_rule ::= #my_hook_char('\t')
            ;
        """)
        res = bnf.get_rules()
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertIsInstance(res['the_rule'], parsing.Hook)
        self.assertTrue(res['the_rule'].name == "my_hook_char")
        dummyData = parsing.Parser()
        dummyData.set_rules(res)
        dummyData.test = self
        self.assertTrue(dummyData.eval_rule('the_rule'))

    def test_21_hookOneParamNum(self):
        @meta.hook(parsing.Parser)
        def my_hook_num(self, num):
            self.test.assertEqual(num, 123456,
                                  'failed to receive 123456 in hook')
            self.test.assertTrue(num == 123456)
            return True

        bnf = dsl.EBNF("""
            the_rule ::= #my_hook_num(123456)
            ;
        """)
        res = bnf.get_rules()
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertIsInstance(res['the_rule'], parsing.Hook)
        self.assertTrue(res['the_rule'].name == "my_hook_num")
        dummyData = parsing.Parser()
        dummyData.set_rules(res)
        dummyData.test = self
        self.assertTrue(dummyData.eval_rule('the_rule'))

    def test_22_hookOneParamId(self):
        @meta.hook(parsing.Parser)
        def my_hook_id(self, n):
            self.test.assertIsInstance(n, parsing.Node)
            return True

        bnf = dsl.EBNF("""
            the_rule ::= #my_hook_id(_)
            ;
        """)
        res = bnf.get_rules()
        self.assertTrue('the_rule' in res)
        self.assertIsInstance(res['the_rule'], parsing.Hook)
        self.assertTrue(res['the_rule'].name == "my_hook_id")
        dummyData = parsing.Parser()
        dummyData.set_rules(res)
        dummyData.test = self
        self.assertTrue(dummyData.eval_rule('the_rule'))

    def test_23_hookParams(self):
        @meta.hook(parsing.Parser)
        def my_hook_params(self, n, num, txt):
            self.test.assertIsInstance(n, parsing.Node)
            self.test.assertTrue(num == 123456)
            self.test.assertTrue(txt == "cool")
            return True

        bnf = dsl.EBNF("""
            the_rule ::= #my_hook_params(_, 123456, "cool")
            ;
        """)
        res = bnf.get_rules()
        self.assertTrue('the_rule' in res)
        self.assertIsInstance(res['the_rule'], parsing.Hook)
        self.assertTrue(res['the_rule'].name == "my_hook_params")
        dummyData = parsing.Parser()
        dummyData.set_rules(res)
        dummyData.test = self
        self.assertTrue(dummyData.eval_rule('the_rule'))

    def test_24_hookAndCapture(self):
        @meta.hook(parsing.Parser)
        def my_hook_multi(self, n1, n2, n3):
            self.test.assertTrue(n1.value == "456")
            self.test.assertTrue(n2.value == '"toto"')
            self.test.assertTrue(n3.value == "blabla")
            return True

        bnf = dsl.EBNF("""

            N ::= Base.num
            ;

            S ::= Base.string
            ;

            I ::= Base.id
            ;

            the_rule ::= N:nth S:t I:i
                         #my_hook_multi(nth, t, i)
            ;
        """)
        res = bnf.get_rules()
        self.assertTrue('the_rule' in res)
        self.assertIsInstance(res['the_rule'], parsing.Seq)
        self.assertTrue(res['the_rule'].ptlist[-1].name == "my_hook_multi")
        dummyData = parsing.Parser("""
            456    "toto"        blabla      
            """)
        dummyData.set_rules(res)
        dummyData.test = self
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
            the_rule ::= @toto.dummyDir(1, 2, 3) test
            ;

            test ::= #my_hook Base.eof
            ;
        """)
        res = bnf.get_rules()
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        dummyData = parsing.Parser()
        dummyData.set_rules(res)
        dummyData.test = self
        self.assertTrue(dummyData.eval_rule('the_rule'))

    def test_25_list_id(self):
        @meta.hook(parsing.Parser)
        def in_list(self, ls, ident):
            if not hasattr(ls, 'list'):
                ls.list = []
            ls.list.append(ident.value)
            return True

        bnf = dsl.EBNF("""
        
            I ::= id
            ;

            list ::= [I : i #in_list(_, i) ]+
            ;
        """)
        res = bnf.get_rules()
        self.assertTrue('list' in res)
        dummyData = parsing.Parser("""
            a     b c   d        e   f
        """)
        dummyData.set_rules(res)
        dummyData.test = self
        eval_res = dummyData.eval_rule('list')
        self.assertTrue(eval_res)
        self.assertTrue(eval_res.list[0] == "a")
        self.assertTrue(eval_res.list[1] == "b")
        self.assertTrue(eval_res.list[2] == "c")
        self.assertTrue(eval_res.list[3] == "d")
        self.assertTrue(eval_res.list[4] == "e")
        self.assertTrue(eval_res.list[5] == "f")

