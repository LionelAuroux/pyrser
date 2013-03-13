import unittest

from pyrser import parsing
from pyrser import dsl


class InternalDsl_Test(unittest.TestCase):
    def test_01_one_rule(self):
        """
        Test default
        """
        bnf = dsl.Parser("""
            the_rule ::= a
            ;
        """)
        res = bnf.evalRule('bnf_dsl')
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertIsInstance(
            res['the_rule'],
            parsing.Rule,
            "failed in ParserTree type for node parsing.Rule")
        self.assertEqual(res['the_rule'].name, "a",
                         "failed in ParserTree type for node parsing.Rule")

    def test_02_two_rules(self):
        """
        Test default
        """
        bnf = dsl.Parser("""
            the_rule ::= a b
            ;
        """)
        res = bnf.evalRule('bnf_dsl')
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertIsInstance(
            res['the_rule'],
            parsing.Clauses,
            "failed in ParserTree type for node parsing.Clauses")
        self.assertIsInstance(
            res['the_rule'].clauses[0],
            parsing.Rule,
            "failed in ParserTree type for node parsing.Rule")
        self.assertEqual(res['the_rule'].clauses[0].name, "a",
                         "failed in name of rule 'a'")
        self.assertIsInstance(
            res['the_rule'].clauses[1],
            parsing.Rule,
            "failed in ParserTree type for node parsing.Rule")
        self.assertEqual(res['the_rule'].clauses[1].name, "b",
                         "failed in name of rule 'b'")

    def test_03_more_rules(self):
        """
        Test default
        """
        bnf = dsl.Parser("""
            the_rule ::= a b c
            ;
        """)
        res = bnf.evalRule('bnf_dsl')
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertIsInstance(
            res['the_rule'],
            parsing.Clauses,
            "failed in ParserTree type for node parsing.Clauses")
        self.assertIsInstance(
            res['the_rule'].clauses[0],
            parsing.Rule,
            "failed in ParserTree type for node parsing.Rule")
        self.assertEqual(res['the_rule'].clauses[0].name, "a",
                         "failed in name of rule 'a'")
        self.assertIsInstance(
            res['the_rule'].clauses[1],
            parsing.Rule,
            "failed in ParserTree type for node parsing.Rule")
        self.assertEqual(res['the_rule'].clauses[1].name, "b",
                         "failed in name of rule 'b'")
        self.assertIsInstance(
            res['the_rule'].clauses[2],
            parsing.Rule,
            "failed in ParserTree type for node parsing.Rule")
        self.assertEqual(res['the_rule'].clauses[2].name, "c",
                         "failed in name of rule 'c'")

    def test_04_one_alt(self):
        """
        Test default
        """
        bnf = dsl.Parser("""
            the_rule ::= a | b
            ;
        """)
        res = bnf.evalRule('bnf_dsl')
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertIsInstance(
            res['the_rule'],
            parsing.Alt,
            "failed in ParserTree type for node parsing.Alt")
        self.assertIsInstance(
            res['the_rule'].clauses[0],
            parsing.Rule,
            "failed in ParserTree type for node parsing.Rule")
        self.assertEqual(res['the_rule'].clauses[0].name, "a",
                         "failed in name of rule 'a'")
        self.assertIsInstance(
            res['the_rule'].clauses[1],
            parsing.Rule,
            "failed in ParserTree type for node parsing.Rule")
        self.assertEqual(res['the_rule'].clauses[1].name, "b",
                         "failed in name of rule 'b'")

    def test_05_two_alt(self):
        """
        Test default
        """
        bnf = dsl.Parser("""
            the_rule ::= a | b | c
            ;
        """)
        res = bnf.evalRule('bnf_dsl')
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertIsInstance(
            res['the_rule'],
            parsing.Alt,
            "failed in ParserTree type for node parsing.Alt")
        self.assertIsInstance(
            res['the_rule'].clauses[0],
            parsing.Rule,
            "failed in ParserTree type for node parsing.Rule")
        self.assertEqual(res['the_rule'].clauses[0].name, "a",
                         "failed in name of rule 'a'")
        self.assertIsInstance(
            res['the_rule'].clauses[1],
            parsing.Rule,
            "failed in ParserTree type for node parsing.Rule")
        self.assertEqual(res['the_rule'].clauses[1].name, "b",
                         "failed in name of rule 'b'")
        self.assertIsInstance(
            res['the_rule'].clauses[2],
            parsing.Rule,
            "failed in ParserTree type for node parsing.Rule")
        self.assertEqual(res['the_rule'].clauses[2].name, "c",
                         "failed in name of rule 'c'")

    def test_06_char(self):
        """
        Test default
        """
        bnf = dsl.Parser("""
            the_rule ::= 'a'
            ;
        """)
        res = bnf.evalRule('bnf_dsl')
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertIsInstance(
            res['the_rule'],
            parsing.Call,
            "failed in ParserTree type for node parsing.Call")
        self.assertEqual(
            res['the_rule'].callObject.__name__,
            parsing.Parser.readChar.__name__,
            "failed in ParserTree type for call to readChar")
        self.assertEqual(res['the_rule'].params[0], 'a',
                         "failed in ParserTree type for param[0] to 'a'")

    def test_07_string(self):
        """
        Test default
        """
        bnf = dsl.Parser("""
            the_rule ::= "bonjour le monde"
            ;
        """)
        res = bnf.evalRule('bnf_dsl')
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertIsInstance(
            res['the_rule'],
            parsing.Call,
            "failed in ParserTree type for node parsing.Call")
        self.assertEqual(
            res['the_rule'].callObject.__name__,
            parsing.Parser.readText.__name__,
            "failed in ParserTree type for call to readText")
        self.assertEqual(
            res['the_rule'].params[0],
            "bonjour le monde",
            'failed in ParserTree type for param[0] to "bonjour le monde"')

    def test_08_range(self):
        """
        Test default
        """
        bnf = dsl.Parser("""
            the_rule ::= 'a'..'z'
            ;
        """)
        res = bnf.evalRule('bnf_dsl')
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertIsInstance(
            res['the_rule'],
            parsing.Call,
            "failed in ParserTree type for node parsing.Call")
        self.assertEqual(
            res['the_rule'].callObject.__name__,
            parsing.Parser.readRange.__name__,
            "failed in ParserTree type for call to readRange")
        self.assertEqual(res['the_rule'].params[0], 'a',
                         "failed in ParserTree type for param[0] to 'a'")
        self.assertEqual(res['the_rule'].params[1], 'z',
                         "failed in ParserTree type for param[1] to 'z'")

    def test_09_complexe(self):
        """
        Test default
        """
        bnf = dsl.Parser("""
            the_rule ::= 'a'..'z' "tutu" 'a' | a b | z
            ;
        """)
        res = bnf.evalRule('bnf_dsl')
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertIsInstance(res['the_rule'], parsing.Alt,
                              "failed in ParserTree type for node parsing.Alt")
        self.assertIsInstance(
            res['the_rule'].clauses[0],
            parsing.Clauses,
            "failed in ParserTree type for node parsing.Clauses")
        self.assertIsInstance(
            res['the_rule'].clauses[0].clauses[0],
            parsing.Call,
            "failed in ParserTree type for node parsing.Call")
        self.assertEqual(
            res['the_rule'].clauses[0].clauses[0].callObject.__name__,
            parsing.Parser.readRange.__name__,
            "failed in ParserTree type for call to readRange")
        self.assertEqual(res['the_rule'].clauses[0].clauses[0].params[0], 'a',
                         "failed in ParserTree type for params[0] to 'a'")
        self.assertEqual(res['the_rule'].clauses[0].clauses[0].params[1], 'z',
                         "failed in ParserTree type for params[1] to 'z'")
        self.assertIsInstance(
            res['the_rule'].clauses[0].clauses[1],
            parsing.Call,
            "failed in ParserTree type for node parsing.Call")
        self.assertEqual(
            res['the_rule'].clauses[0].clauses[1].callObject.__name__,
            parsing.Parser.readText.__name__,
            "failed in ParserTree type for call to readText")
        self.assertEqual(
            res['the_rule'].clauses[0].clauses[1].params[0],
            "tutu",
            'failed in ParserTree type for params[0] to "tutu"')
        self.assertIsInstance(
            res['the_rule'].clauses[0].clauses[2],
            parsing.Call,
            "failed in ParserTree type for node parsing.Call")
        self.assertEqual(
            res['the_rule'].clauses[0].clauses[2].callObject.__name__,
            parsing.Parser.readChar.__name__,
            "failed in ParserTree type for call to readChar")
        self.assertIsInstance(
            res['the_rule'].clauses[1],
            parsing.Clauses,
            "failed in ParserTree type for node parsing.Clauses")
        self.assertIsInstance(
            res['the_rule'].clauses[1].clauses[0],
            parsing.Rule,
            "failed in ParserTree type for node parsing.Rule")
        self.assertEqual(res['the_rule'].clauses[1].clauses[0].name, "a",
                         "failed in name of rule 'a'")
        self.assertEqual(res['the_rule'].clauses[1].clauses[1].name, "b",
                         "failed in name of rule 'b'")
        self.assertIsInstance(
            res['the_rule'].clauses[2],
            parsing.Rule,
            "failed in ParserTree type for node parsing.Rule")
        self.assertEqual(res['the_rule'].clauses[2].name, "z",
                         "failed in name of rule 'z'")

    def test_10_repoption(self):
        """
        Test default
        """
        bnf = dsl.Parser("""
            the_rule ::= a?
            ;
        """)
        res = bnf.evalRule('bnf_dsl')
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertIsInstance(
            res['the_rule'],
            parsing.RepOptional,
            "failed in ParserTree type for node RepOptional")
        self.assertEqual(res['the_rule'].clause.name, 'a',
                         "failed in name of rule 'a'")

    def test_11_rep0N(self):
        """
        Test default
        """
        bnf = dsl.Parser("""
            the_rule ::= [a]*
            ;
        """)
        res = bnf.evalRule('bnf_dsl')
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertIsInstance(
            res['the_rule'],
            parsing.Rep0N,
            "failed in ParserTree type for node Rep0N")
        self.assertEqual(res['the_rule'].clause.name, 'a',
                         "failed in name of rule 'a'")

    def test_12_rep1N(self):
        """
        Test default
        """
        bnf = dsl.Parser("""
            the_rule ::= [a "toto"]+
            ;
        """)
        res = bnf.evalRule('bnf_dsl')
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertIsInstance(
            res['the_rule'],
            parsing.Rep1N,
            "failed in ParserTree type for node Rep1N")
        self.assertEqual(res['the_rule'].clause.clauses[0].name, 'a',
                         "failed in name of rule 'a'")
        self.assertEqual(res['the_rule'].clause.clauses[1].params[0], "toto",
                         'failed in name of rule "toto"')
