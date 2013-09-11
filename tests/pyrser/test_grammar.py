import unittest
from unittest import mock

import pyrser


class TestGrammar(unittest.TestCase):
    def test_it_parses_a_grammar_and_attach_parsing_rules(self):
        bnf = mock.Mock()
        rule = mock.Mock()
        dsl = mock.Mock()
        dsl.return_value.get_rules.return_value = {'rulename': rule}

        class Grammar(pyrser.Grammar):
            grammar = bnf
            dsl_parser = dsl

        dsl.assert_called_once_with(bnf)
        dsl.return_value.get_rules.assert_called_once_with()
        self.assertIs(rule, Grammar._rules['rulename'])

    def test_it_parses_source_using_rules(self):
        bnf = mock.Mock()
        rule = mock.Mock()
        dsl = mock.Mock()
        dsl.return_value.get_rules.return_value = {'rulename': rule}
        source = mock.Mock()

        class StubGrammar(pyrser.Grammar):
            entry = 'rulename'
            dsl_parser = dsl

        grammar = StubGrammar()
        grammar.parsed_stream = mock.Mock()
        grammar.eval_rule = mock.Mock()
        grammar.parse(source)
        grammar.parsed_stream.assert_call_once_with(source)
        grammar.eval_rule.assert_call_once_with('rulename')

#    def test_it_raises_valueerror_without_entry_rulename(self):
#        class UselessGrammar(pyrser.Grammar):
#            pass
#
#        with self.assertRaises(ValueError):
#            parser = UselessGrammar()

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
