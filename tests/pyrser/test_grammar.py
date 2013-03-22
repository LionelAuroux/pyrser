import unittest
try:
    from unittest import mock
except ImportError:
    import mock

import pyrser


class TestGrammar(unittest.TestCase):
    def test_it_parses_a_grammar_and_attach_parsing_rules(self):
        bnf = mock.Mock()
        rules = {'rule0': mock.Mock(), 'rule1': mock.Mock()}
        parser = mock.Mock(**{'parse.return_value': rules})
        dsl = mock.Mock(return_value=parser)

        class Grammar(pyrser.Grammar):
            grammar = bnf
            dsl_parser = dsl

        dsl.assert_called_once_with(bnf)
        parser.parse.assert_called_once_with()
        self.assertEqual(rules, Grammar.rules)

    def test_it_parses_source_using_rules(self):
        source, res = mock.Mock(), mock.Mock()
        rules = mock.Mock()
        parser = mock.Mock(**{'setRules.return_value': None,
                              'evalRule.return_value': res})
        with mock.patch('pyrser.grammar.parsing.Parser',
                        return_value=parser) as parser_cls:
            class StubGrammar(pyrser.Grammar):
                entry = 'rulename'

            StubGrammar.rules = rules
            grammar = StubGrammar()
            self.assertEqual(res, grammar.parse(source))
            parser_cls.assert_called_once_with(source)
            parser.setRules.assert_called_once_with(rules)
            parser.evalRule.assert_called_once_with('rulename')

    def test_it_raises_valueerror_without_entry_rulename(self):
        class UselessGrammar(pyrser.Grammar):
            pass
        with self.assertRaises(ValueError):
            parser = UselessGrammar()

#    def test_it_aggregates_grammar(self):
#        class AbstractKeywordGrammar(pyrser.Grammar):
#            grammar = '''kw ::= "keyword" eof;'''
#
#        class AbstractClassGrammar(pyrser.Grammar):
#            grammar = '''class ::= "class" kw;'''
#
#        class GrammarCombination(AbstractClassGrammar,
#                                 AbstractKeywordGrammar):
#            entry = 'class'
#
#        class OverrideClassKeywordGrammar(GrammarCombination):
#            grammar = '''kw ::= "keys" ';' eof;'''
#
#        parser = GrammarCombination()
#        self.assertTrue(parser.parse("class keyword"))
#        parser = OverrideClassKeywordGrammar()
#        self.assertTrue(parser.parse("class keys;"))
