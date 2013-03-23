import unittest

from pyrser import parsing
from pyrser import dsl
from pyrser.parsing import node
from pyrser import meta

class InternalDsl_Test(unittest.TestCase):
    def test_01_one_rule(self):
        """
        Test default
        """
        bnf = dsl.Parser("""
            the_rule ::= a
            ;
        """)
        res = bnf.eval_rule('bnf_dsl')
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertIsInstance(res['the_rule'], parsing.Rule, "failed in ParserTree type for node Rule")
        self.assertTrue(res['the_rule'].name == "a", "failed in ParserTree type for node Rule")

    def test_02_two_rules(self):
        """
        Test default
        """
        bnf = dsl.Parser("""
            the_rule ::= a b
            ;
        """)
        res = bnf.eval_rule('bnf_dsl')
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertIsInstance(res['the_rule'], parsing.Seq, "failed in ParserTree type for node Seq")
        self.assertIsInstance(res['the_rule'].ptlist[0], parsing.Rule, "failed in ParserTree type for node Rule")
        self.assertTrue(res['the_rule'].ptlist[0].name == "a", "failed in name of rule 'a'")
        self.assertIsInstance(res['the_rule'].ptlist[1], parsing.Rule, "failed in ParserTree type for node Rule")
        self.assertTrue(res['the_rule'].ptlist[1].name == "b", "failed in name of rule 'b'")

    def test_03_more_rules(self):
        """
        Test default
        """
        bnf = dsl.Parser("""
            the_rule ::= a b c
            ;
        """)
        res = bnf.eval_rule('bnf_dsl')
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertIsInstance(res['the_rule'], parsing.Seq, "failed in ParserTree type for node Seq")
        self.assertIsInstance(res['the_rule'].ptlist[0], parsing.Rule, "failed in ParserTree type for node Rule")
        self.assertTrue(res['the_rule'].ptlist[0].name == "a", "failed in name of rule 'a'")
        self.assertIsInstance(res['the_rule'].ptlist[1], parsing.Rule, "failed in ParserTree type for node Rule")
        self.assertTrue(res['the_rule'].ptlist[1].name == "b", "failed in name of rule 'b'")
        self.assertIsInstance(res['the_rule'].ptlist[2], parsing.Rule, "failed in ParserTree type for node Rule")
        self.assertTrue(res['the_rule'].ptlist[2].name == "c", "failed in name of rule 'c'")

    def test_04_one_alt(self):
        """
        Test default
        """
        bnf = dsl.Parser("""
            the_rule ::= a | b
            ;
        """)
        res = bnf.eval_rule('bnf_dsl')
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertIsInstance(res['the_rule'], parsing.Alt, "failed in ParserTree type for node Alt")
        self.assertIsInstance(res['the_rule'].ptlist[0], parsing.Rule, "failed in ParserTree type for node Rule")
        self.assertTrue(res['the_rule'].ptlist[0].name == "a", "failed in name of rule 'a'")
        self.assertIsInstance(res['the_rule'].ptlist[1], parsing.Rule, "failed in ParserTree type for node Rule")
        self.assertTrue(res['the_rule'].ptlist[1].name == "b", "failed in name of rule 'b'")

    def test_05_two_alt(self):
        """
        Test default
        """
        bnf = dsl.Parser("""
            the_rule ::= a | b | c
            ;
        """)
        res = bnf.eval_rule('bnf_dsl')
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertIsInstance(res['the_rule'], parsing.Alt, "failed in ParserTree type for node Alt")
        self.assertIsInstance(res['the_rule'].ptlist[0], parsing.Rule, "failed in ParserTree type for node Rule")
        self.assertTrue(res['the_rule'].ptlist[0].name == "a", "failed in name of rule 'a'")
        self.assertIsInstance(res['the_rule'].ptlist[1], parsing.Rule, "failed in ParserTree type for node Rule")
        self.assertTrue(res['the_rule'].ptlist[1].name == "b", "failed in name of rule 'b'")
        self.assertIsInstance(res['the_rule'].ptlist[2], parsing.Rule, "failed in ParserTree type for node Rule")
        self.assertTrue(res['the_rule'].ptlist[2].name == "c", "failed in name of rule 'c'")

    def test_06_char(self):
        """
        Test default
        """
        bnf = dsl.Parser("""
            the_rule ::= 'a'
            ;
        """)
        res = bnf.eval_rule('bnf_dsl')
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertIsInstance(res['the_rule'], parsing.Call, "failed in ParserTree type for node Call")
        self.assertTrue(res['the_rule'].callObject.__name__ == parsing.Parser.read_char.__name__, "failed in ParserTree type for call to readChar")
        self.assertTrue(res['the_rule'].params[0] == 'a', "failed in ParserTree type for params[0] to 'a'")

    def test_07_string(self):
        """
        Test default
        """
        bnf = dsl.Parser("""
            the_rule ::= "bonjour le monde"
            ;
        """)
        res = bnf.eval_rule('bnf_dsl')
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertIsInstance(res['the_rule'], parsing.Call, "failed in ParserTree type for node Call")
        self.assertTrue(res['the_rule'].callObject.__name__ == parsing.Parser.read_text.__name__, "failed in ParserTree type for call to read_text")
        self.assertTrue(res['the_rule'].params[0] == "bonjour le monde", 'failed in ParserTree type for params[0] to "bonjour le monde"')

    def test_08_range(self):
        """
        Test default
        """
        bnf = dsl.Parser("""
            the_rule ::= 'a'..'z'
            ;
        """)
        res = bnf.eval_rule('bnf_dsl')
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertIsInstance(res['the_rule'], parsing.Call, "failed in ParserTree type for node Call")
        self.assertTrue(res['the_rule'].callObject.__name__ == parsing.Parser.read_range.__name__, "failed in ParserTree type for call to read_range")
        self.assertTrue(res['the_rule'].params[0] == 'a', "failed in ParserTree type for params[0] to 'a'")
        self.assertTrue(res['the_rule'].params[1] == 'z', "failed in ParserTree type for params[1] to 'z'")

    def test_09_complexe(self):
        """
        Test default
        """
        bnf = dsl.Parser("""
            the_rule ::= 'a'..'z' "tutu" 'a' | a b | z
            ;
        """)
        res = bnf.eval_rule('bnf_dsl')
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertIsInstance(res['the_rule'], parsing.Alt, "failed in ParserTree type for node Alt")
        self.assertIsInstance(res['the_rule'].ptlist[0], parsing.Seq, "failed in ParserTree type for node Seq")
        self.assertIsInstance(res['the_rule'].ptlist[0].ptlist[0], parsing.Call, "failed in ParserTree type for node Call")
        self.assertTrue(res['the_rule'].ptlist[0].ptlist[0].callObject.__name__ == parsing.Parser.read_range.__name__, "failed in ParserTree type for call to read_range")
        self.assertTrue(res['the_rule'].ptlist[0].ptlist[0].params[0] == 'a', "failed in ParserTree type for params[0] to 'a'")
        self.assertTrue(res['the_rule'].ptlist[0].ptlist[0].params[1] == 'z', "failed in ParserTree type for params[1] to 'z'")
        self.assertIsInstance(res['the_rule'].ptlist[0].ptlist[1], parsing.Call, "failed in ParserTree type for node Call")
        self.assertTrue(res['the_rule'].ptlist[0].ptlist[1].callObject.__name__ == parsing.Parser.read_text.__name__, "failed in ParserTree type for call to read_text")
        self.assertTrue(res['the_rule'].ptlist[0].ptlist[1].params[0] == "tutu", 'failed in ParserTree type for params[0] to "tutu"')
        self.assertIsInstance(res['the_rule'].ptlist[0].ptlist[2], parsing.Call, "failed in ParserTree type for node Call")
        self.assertTrue(res['the_rule'].ptlist[0].ptlist[2].callObject.__name__ == parsing.Parser.read_char.__name__, "failed in ParserTree type for call to read_char")
        self.assertIsInstance(res['the_rule'].ptlist[1], parsing.Seq, "failed in ParserTree type for node Seq")
        self.assertIsInstance(res['the_rule'].ptlist[1].ptlist[0], parsing.Rule, "failed in ParserTree type for node Rule")
        self.assertTrue(res['the_rule'].ptlist[1].ptlist[0].name == "a", "failed in name of rule 'a'")
        self.assertTrue(res['the_rule'].ptlist[1].ptlist[1].name == "b", "failed in name of rule 'b'")
        self.assertIsInstance(res['the_rule'].ptlist[2], parsing.Rule, "failed in ParserTree type for node Rule")
        self.assertTrue(res['the_rule'].ptlist[2].name == "z", "failed in name of rule 'z'")

    def test_10_repoption(self):
        """
        Test default
        """
        bnf = dsl.Parser("""
            the_rule ::= a?
            ;
        """)
        res = bnf.eval_rule('bnf_dsl')
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertIsInstance(res['the_rule'], parsing.RepOptional, "failed in ParserTree type for node RepOptional")
        self.assertTrue(res['the_rule'].pt.name == 'a', "failed in name of rule 'a'")

    def test_11_rep0N(self):
        """
        Test default
        """
        bnf = dsl.Parser("""
            the_rule ::= [a]*
            ;
        """)
        res = bnf.eval_rule('bnf_dsl')
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertIsInstance(res['the_rule'], parsing.Rep0N, "failed in ParserTree type for node Rep0N")
        self.assertTrue(res['the_rule'].pt.name == 'a', "failed in name of rule 'a'")

    def test_12_rep1N(self):
        """
        Test default
        """
        bnf = dsl.Parser("""
            the_rule ::= [a "toto"]+
            ;
        """)
        res = bnf.eval_rule('bnf_dsl')
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertIsInstance(res['the_rule'], parsing.Rep1N, "failed in ParserTree type for node Rep1N")
        self.assertTrue(res['the_rule'].pt.ptlist[0].name == 'a', "failed in name of rule 'a'")
        self.assertTrue(res['the_rule'].pt.ptlist[1].params[0] == "toto", 'failed in name of rule "toto"')

    def test_13_hookNoParam(self):
        bnf = dsl.Parser("""
            the_rule ::= #hook
            ;
        """)
        res = bnf.eval_rule('bnf_dsl')
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertIsInstance(res['the_rule'], parsing.Hook, "failed in ParserTree type for node Hook")

    def test_14_hookOneParamStr(self):
        @meta.hook(parsing.Parser)
        def my_hook_txt(self, txt):
            self.test.assertTrue(txt == "cool", 'failed to receive "cool" in hook')
            return True
        bnf = dsl.Parser("""
            the_rule ::= #my_hook_txt("cool")
            ;
        """)
        res = bnf.eval_rule('bnf_dsl')
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertIsInstance(res['the_rule'], parsing.Hook, "failed in ParserTree type for node Hook")
        self.assertTrue(res['the_rule'].name == "my_hook_txt", "failed in name of hook 'my_hook_txt'")
        dummyData = parsing.Parser()
        dummyData.set_rules(res)
        dummyData.test = self
        self.assertTrue(dummyData.eval_rule('the_rule'), "failed to parse dummyData")

    def test_15_hookOneParamChar(self):
        @meta.hook(parsing.Parser)
        def my_hook_char(self, txt):
            self.test.assertTrue(txt == "\t", 'failed to receive "\t" in hook')
            return True
        bnf = dsl.Parser("""
            the_rule ::= #my_hook_char('\t')
            ;
        """)
        res = bnf.eval_rule('bnf_dsl')
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertIsInstance(res['the_rule'], parsing.Hook, "failed in ParserTree type for node Hook")
        self.assertTrue(res['the_rule'].name == "my_hook_char", "failed in name of hook 'my_hook_char'")
        dummyData = parsing.Parser()
        dummyData.set_rules(res)
        dummyData.test = self
        self.assertTrue(dummyData.eval_rule('the_rule'), "failed to parse dummyData")

    def test_16_hookOneParamNum(self):
        @meta.hook(parsing.Parser)
        def my_hook_num(self, num):
            self.test.assertTrue(num == 123456, 'failed to receive 123456 in hook')
            return True
        bnf = dsl.Parser("""
            the_rule ::= #my_hook_num(123456)
            ;
        """)
        res = bnf.eval_rule('bnf_dsl')
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertIsInstance(res['the_rule'], parsing.Hook, "failed in ParserTree type for node Hook")
        self.assertTrue(res['the_rule'].name == "my_hook_num", "failed in name of hook 'my_hook_num'")
        dummyData = parsing.Parser()
        dummyData.set_rules(res)
        dummyData.test = self
        self.assertTrue(dummyData.eval_rule('the_rule'), "failed to parse dummyData")

    def test_17_hookOneParamId(self):
        @meta.hook(parsing.Parser)
        def my_hook_id(self, n):
            self.test.assertIsInstance(n, node.Node, 'failed to receive node in hook')
            return True
        bnf = dsl.Parser("""
            the_rule ::= #my_hook_id(the_rule)
            ;
        """)
        res = bnf.eval_rule('bnf_dsl')
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertIsInstance(res['the_rule'], parsing.Hook, "failed in ParserTree type for node Hook")
        self.assertTrue(res['the_rule'].name == "my_hook_id", "failed in name of hook 'my_hook_id'")
        dummyData = parsing.Parser()
        dummyData.set_rules(res)
        dummyData.test = self
        self.assertTrue(dummyData.eval_rule('the_rule'), "failed to parse dummyData")

    def test_18_hookParams(self):
        @meta.hook(parsing.Parser)
        def my_hook_params(self, n, num, txt):
            self.test.assertIsInstance(n, node.Node, 'failed to receive node in hook')
            self.test.assertTrue(num == 123456, 'failed to receive 123456 in hook')
            self.test.assertTrue(txt == "cool", 'failed to receive "cool" in hook')
            return True
        bnf = dsl.Parser("""
            the_rule ::= #my_hook_params(the_rule, 123456, "cool")
            ;
        """)
        res = bnf.eval_rule('bnf_dsl')
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertIsInstance(res['the_rule'], parsing.Hook, "failed in ParserTree type for node Hook")
        self.assertTrue(res['the_rule'].name == "my_hook_params", "failed in name of hook 'my_hook_params'")
        dummyData = parsing.Parser()
        dummyData.set_rules(res)
        dummyData.test = self
        self.assertTrue(dummyData.eval_rule('the_rule'), "failed to parse dummyData")

    def test_19_hookAndCapture(self):
        @meta.hook(parsing.Parser)
        def my_hook_multi(self, n1, n2, n3):
            self.test.assertTrue(n1.value == "456", 'failed to receive 456 in hook')
            self.test.assertTrue(n2.value == "toto", 'failed to receive "toto" in hook')
            self.test.assertTrue(n3.value == "blabla", 'failed to receive "blabla" in hook')
            return True
        bnf = dsl.Parser("""
            the_rule ::= Base.num : nth Base.string : t Base.id : i #my_hook_multi(nth, t, i)
            ;
        """)
        res = bnf.eval_rule('bnf_dsl')
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertIsInstance(res['the_rule'], parsing.Seq, "failed in ParserTree type for node Seq")
        self.assertTrue(res['the_rule'].ptlist[-1].name == "my_hook_multi", "failed in name of hook 'my_hook_multi'")
        dummyData = parsing.Parser("""
            456 "toto" blabla
            """)
        dummyData.set_rules(res)
        dummyData.test = self
        self.assertTrue(dummyData.eval_rule('the_rule'), "failed to parse dummyData")

    def test_20_directive(self):
        class dummyDir(parsing.DirectiveWrapper):
            def begin(self, parser, a: int, b: int, c: int):
                parser.test.assertTrue(a == 1, "failed in recv parameter in begin method expected 1 recv %s" % a)
                parser.test.assertTrue(b == 2, "failed in recv parameter in begin method expected 2 recv %s" % b)
                parser.test.assertTrue(c == 3, "failed in recv parameter in begin method expected 3 recv %s" % c)
                # for workflow checking
                parser.workflow = 1
                return True
            def end(self, parser, a: int, b: int, c: int):
                parser.test.assertTrue(a == 1, "failed in recv parameter in end method expected 1 recv %s" % a)
                parser.test.assertTrue(b == 2, "failed in recv parameter in end method expected 2 recv %s" % b)
                parser.test.assertTrue(c == 3, "failed in recv parameter in end method expected 3 recv %s" % c)
                # for workflow checking
                parser.test.assertTrue(parser.workflow == 2, "failed my_hook was not called before end")
                return True
        @meta.hook(parsing.Parser)
        def my_hook(self):
            # for workflow checking
            self.test.assertTrue(self.workflow == 1, "failed begin was not called before my_hook")
            self.workflow = 2
            return True
        dsl.Parser.set_directives({'toto.dummyDir' : dummyDir})
        bnf = dsl.Parser("""
            the_rule ::= @toto.dummyDir(1, 2, 3) test
            ;

            test ::= #my_hook Base.eof
            ;
        """)
        res = bnf.eval_rule('bnf_dsl')
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        dummyData = parsing.Parser()
        dummyData.set_rules(res)
        dummyData.test = self
        self.assertTrue(dummyData.eval_rule('the_rule'), "failed to parse dummyData")

