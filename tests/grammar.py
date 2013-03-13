import unittest

import pyrser


class TestGrammar(unittest.TestCase):
    def test_it_parses_a_keyword(self):
        class KeywordGrammar(pyrser.Grammar):
            #grammar = '''kw ::= "keyword" Base::eof;'''
            grammar = '''kw ::= "keyword" eof;'''
            entry = 'kw'

        parser = KeywordGrammar()
        self.assertTrue(parser.parse(" keyword "))

    def test_it_aggregates_grammar(self):
        class AbstractKeywordGrammar(pyrser.Grammar):
            grammar = '''kw ::= "keyword" eof;'''

        class AbstractClassGrammar(pyrser.Grammar):
            grammar = '''class ::= "class" kw;'''

        class GrammarCombination(AbstractClassGrammar,
                                 AbstractKeywordGrammar):
            entry = 'class'

        class OverrideClassKeywordGrammar(GrammarCombination):
            grammar = '''kw ::= "keys" ';' eof;'''

        parser = GrammarCombination()
        self.assertTrue(parser.parse("class keyword"))
        parser = OverrideClassKeywordGrammar()
        self.assertTrue(parser.parse("class keys;"))
