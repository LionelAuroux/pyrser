from collections import ChainMap
import unittest

from pyrser import grammar
from pyrser import meta
from pyrser import parsing
from pyrser import error
from pyrser.hooks import copy
from pyrser.directives import ignore

import weakref
from pyrser.passes import dumpParseTree

class WordList(grammar.Grammar):
    grammar = """
        wordlist ::= [word : w #add_to(_, w)]+ eof
        ;

        word ::= @ignore("null") ['a'..'z'|'A'..'Z']+
        ;
    """
    entry = "wordlist"


class CSV(grammar.Grammar):
    entry = "csv"
    grammar = """
        csv ::= [@ignore("null") line : l #add_line(_, l)]+ eof
        ;

        line ::= item : c #add_col(_, c)
            [';' item : c #add_col(_, c)]*
            eol
        ;

        item ::= [id | num] : i #add_item(_, i)
        ;
    """


class CSV2(grammar.Grammar, CSV):
    entry = "csv2"
    # copy the result of CSV.csv as result of csv2
    grammar = """
        csv2 ::= CSV.csv:_
        ;

        item ::= [CSV.item]?:_
        ;
    """


class DummyCpp(grammar.Grammar):
    entry = "main"
    grammar = """
        main ::= @ignore("C/C++") [id:i #copy(_, i)]+
        ;
    """


class GrammarBasic_Test(unittest.TestCase):
    def test_01_list_word(self):
        """
        Test List Word
        """
        @meta.hook(WordList)
        def add_to(self, mylist, word):
            if not hasattr(mylist, 'lst'):
                mylist.lst = [word.value]
            else:
                mylist.lst.append(word.value)
            return True

        ws = WordList("ab cd ef gh")
        res = ws.parse()
        self.assertTrue(res, "failed to parse WordList")
        self.assertEqual(res.lst[2], "ef", "failed to reach lst[2]")

    def test_02_csv(self):
        """
        Test CSV
        """
        @meta.hook(CSV)
        def add_line(self, csv, l):
            if not hasattr(csv, 'tab'):
                csv.tab = [l.cols]
            else:
                csv.tab.append(l.cols)
            return True

        @meta.hook(CSV)
        def add_col(self, line, c):
            if not hasattr(line, 'cols'):
                line.cols = [c.value]
            else:
                line.cols.append(c.value)
            return True

        @meta.hook(CSV)
        def add_item(self, item, i):
            item.value = i.value
            return True

        csv = CSV()
        res = csv.parse("""
        1;a;3;b;5
        l;r
        o
        4;1
        7;u;p
        """)
        self.assertTrue(res, "failed to parse CSV")
        self.assertEqual(res.tab[2][0], "o", "failed to reach tab[2][0]")
        self.assertEqual(res.tab[4][1], "u", "failed to reach tab[4][1]")

    def test_03_inherit_csv(self):
        """
        Test CSV2
        """
        csv2 = CSV2()
        res = csv2.parse("""
        3;;2;;1
        ;
        ;1
        6;;8
        """)
        self.assertTrue(res, "failed to parse CSV2")
        self.assertEqual(res.tab[0][2], "2", "failed to reach tab[0][2]")
        self.assertEqual(res.tab[1][0], "",
                         "failed to reach tab[1][0] as empty string")
        self.assertEqual(res.tab[1][1], "",
                         "failed to reach tab[1][1] as empty string")

    def test_04_parse_error_csv(self):
        """
        Test parser error in CSV
        """
        csv = CSV()
        with self.assertRaises(error.ParseError) as pe:
            res = csv.parse("""
            1;2;3;4
            a;b;c;';4;5
            o;l;p
            """)
        self.assertEqual(pe.exception.error_position.col_offset, 19,
                         "failed to get the correct position")

    def test_05_parse_error_dsl(self):
        """
        Test parser error in the DSL
        """
        with self.assertRaises(error.ParseError) as pe:
            class TestDsl(grammar.Grammar):
                grammar = """
                    not_finished_bnf"""
                entry = "not_finished_bnf"
        self.assertEqual(pe.exception.raw_msg, "Expected '::='",
                         "failed to get the correct message")
        self.assertEqual(pe.exception.error_position.col_offset, 37,
                         "failed to get the correct position")

    def test_06_parse_error_dsl(self):
        """
        Test parser error in the DSL
        """
        with self.assertRaises(error.ParseError) as pe:
            class TestDsl(grammar.Grammar):
                grammar = """
                    not_finished_bnf ::= clause"""
                entry = "not_finished_bnf"
        self.assertEqual(pe.exception.raw_msg, "Expected ';'",
                         "failed to get the correct message")
        self.assertEqual(pe.exception.error_position.col_offset, 48,
                         "failed to get the correct position")

    def test_07_parse_error_dsl(self):
        """
        Test parser error in the DSL
        """
        with self.assertRaises(error.ParseError) as pe:
            class TestDsl(grammar.Grammar):
                grammar = """
                    not_finished_bnf ::= #hook(12"""
                entry = "not_finished_bnf"
        self.assertEqual(pe.exception.raw_msg, "Expected ')'",
                         "failed to get the correct message")
        self.assertEqual(pe.exception.error_position.col_offset, 50,
                         "failed to get the correct position")

    def test_08_parse_error_dsl(self):
        """
        Test parser error in the DSL
        """
        with self.assertRaises(error.ParseError) as pe:
            class TestDsl(grammar.Grammar):
                grammar = """
                    not_finished_bnf ::= @dir(12"""
                entry = "not_finished_bnf"
        self.assertEqual(pe.exception.raw_msg, "Expected ')'",
                         "failed to get the correct message")
        self.assertEqual(pe.exception.error_position.col_offset, 49,
                         "failed to get the correct position")

    def test_09_parse_error_dsl(self):
        """
        Test parser error in the DSL
        """
        with self.assertRaises(error.ParseError) as pe:
            class TestDsl(grammar.Grammar):
                grammar = """
                    not_finished_bnf ::= #hook(12,"""
                entry = "not_finished_bnf"
        self.assertEqual(pe.exception.raw_msg, "Expected parameter",
                         "failed to get the correct message")
        self.assertEqual(pe.exception.error_position.col_offset, 51,
                         "failed to get the correct position")

    def test_10_parse_error_dsl(self):
        """
        Test parser error in the DSL
        """
        with self.assertRaises(error.ParseError) as pe:
            class TestDsl(grammar.Grammar):
                grammar = """
                    not_finished_bnf ::= #hook("""
                entry = "not_finished_bnf"
        self.assertEqual(pe.exception.raw_msg, "Expected parameter",
                         "failed to get the correct message")
        self.assertEqual(pe.exception.error_position.col_offset, 48,
                         "failed to get the correct position")

    def test_11_parse_error_dsl(self):
        """
        Test parser error in the DSL
        """
        with self.assertRaises(error.ParseError) as pe:
            class TestDsl(grammar.Grammar):
                grammar = """
                    not_finished_bnf ::= @dir(12,"""
                entry = "not_finished_bnf"
        self.assertEqual(pe.exception.raw_msg, "Expected parameter",
                         "failed to get the correct message")
        self.assertEqual(pe.exception.error_position.col_offset, 50,
                         "failed to get the correct position")

    def test_12_parse_error_dsl(self):
        """
        Test parser error in the DSL
        """
        with self.assertRaises(error.ParseError) as pe:
            class TestDsl(grammar.Grammar):
                grammar = """
                    not_finished_bnf ::= @dir("""
                entry = "not_finished_bnf"
        self.assertEqual(pe.exception.raw_msg, "Expected parameter",
                         "failed to get the correct message")
        self.assertEqual(pe.exception.error_position.col_offset, 47,
                         "failed to get the correct position")

    def test_13_parse_error_dsl(self):
        """
        Test parser error in the DSL
        """
        with self.assertRaises(error.ParseError) as pe:
            class TestDsl(grammar.Grammar):
                grammar = """
                    not_finished_bnf ::= [a"""
                entry = "not_finished_bnf"
        self.assertEqual(pe.exception.raw_msg, "Expected ']'",
                         "failed to get the correct message")
        self.assertEqual(pe.exception.error_position.col_offset, 44,
                         "failed to get the correct position")

    def test_14_parse_error_dsl(self):
        """
        Test parser error in the DSL
        """
        with self.assertRaises(error.ParseError) as pe:
            class TestDsl(grammar.Grammar):
                grammar = """
                    not_finished_bnf ::= ["""
                entry = "not_finished_bnf"
        self.assertEqual(pe.exception.raw_msg, "Expected sequences",
                         "failed to get the correct message")
        self.assertEqual(pe.exception.error_position.col_offset, 43,
                         "failed to get the correct position")

    def test_15_ignore_cpp(self):
        """
        Test ignore directive for C/C++
        """
        cxx = DummyCpp()
        res = cxx.parse("""
            a b c /* comment */
            // another comment
            d e/**/f//
            g
        """)
        self.assertTrue(res, "failed to parse dummyCpp")
        self.assertEqual(res.value, 'g', "failed to parse comments")
