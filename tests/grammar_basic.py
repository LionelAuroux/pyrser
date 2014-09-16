import unittest
import os
from pyrser import grammar
from pyrser import meta
from pyrser import parsing
from pyrser import error
from pyrser.passes.to_yml import *
from pyrser.directives import ignore

from tests.grammar.csv import *


class WordList(grammar.Grammar):
    grammar = """
        wordlist =[ [word : w #add_to(_, w)]+ eof ]

        word =[ @ignore("null") ['a'..'z'|'A'..'Z']+ ]
    """
    entry = "wordlist"


class DummyCpp(grammar.Grammar):
    entry = "main"
    grammar = """
        main =[ @ignore("C/C++") [id:i #add(_, i)]+ ]
    """


class GrammarBasic_Test(unittest.TestCase):
    def test_01_list_word(self):
        """
        Test List Word
        """
        @meta.hook(WordList)
        def add_to(self, mylist, word):
            if not hasattr(mylist, 'lst'):
                mylist.lst = [self.value(word)]
            else:
                mylist.lst.append(self.value(word))
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
            item.value = self.value(i)
            return True

        csv = CSV()
        if csv:
            txt = """
            1;a;3;b;5
            l;r
            o
            4;1
            7;u;p
            """
            res = csv.parse(txt)
            self.assertTrue(res, "failed to parse CSV")
            self.assertEqual(res.tab[2][0], "o", "failed to reach tab[2][0]")
            self.assertEqual(res.tab[4][1], "u", "failed to reach tab[4][1]")

    def test_03_inherit_csv(self):
        """
        Test CSV2
        """
        @meta.hook(CSV2)
        def add_col(self, line, c):
            colval = ''
            if hasattr(c, 'value'):
                colval = c.value
            if not hasattr(line, 'cols'):
                line.cols = [colval]
            else:
                line.cols.append(colval)
            return True
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
        res = csv.parse("""
            1;2;3;4
            8;9;10;11
            a;b;c;';4;5
            o;l;p
        """)
        self.assertFalse(res, "Failed to detect the error")
        s = res.diagnostic.get_content()
        self.assertEqual(
            res.diagnostic.logs[0].msg,
            "Parse error in 'eof'",
            "Bad message in Diagnostic"
        )
        self.assertEqual(
            res.diagnostic.logs[0].location.line,
            4,
            "Bad line in Diagnostic"
        )
        self.assertEqual(
            res.diagnostic.logs[0].location.col,
            19,
            "Bad line in Diagnostic"
        )

    def test_05_parse_error_dsl(self):
        """
        Test parser error in the DSL
        """
        with self.assertRaises(error.Diagnostic) as pe:
            class TestDsl(grammar.Grammar):
                grammar = """
                    not_finished_bnf"""
                entry = "not_finished_bnf"
        self.assertEqual(pe.exception.logs[0].msg, "Expected '='",
                         "failed to get the correct message")
        self.assertEqual(pe.exception.logs[0].location.col, 37,
                         "failed to get the correct position")

    def test_06_parse_error_dsl(self):
        """
        Test parser error in the DSL
        """
        with self.assertRaises(error.Diagnostic) as pe:
            class TestDsl(grammar.Grammar):
                grammar = """
                    not_finished_bnf = [ clause"""
                entry = "not_finished_bnf"
        self.assertEqual(pe.exception.logs[0].msg, "Expected ']'",
                         "failed to get the correct message")
        self.assertEqual(pe.exception.logs[0].location.col, 48,
                         "failed to get the correct position")

    def test_07_parse_error_dsl(self):
        """
        Test parser error in the DSL
        """
        with self.assertRaises(error.Diagnostic) as pe:
            class TestDsl(grammar.Grammar):
                grammar = """
                    not_finished_bnf =[ #hook(12"""
                entry = "not_finished_bnf"
        self.assertEqual(pe.exception.logs[0].msg, "Expected ')'",
                         "failed to get the correct message")
        self.assertEqual(pe.exception.logs[0].location.col, 49,
                         "failed to get the correct position")

    def test_08_parse_error_dsl(self):
        """
        Test parser error in the DSL
        """
        with self.assertRaises(error.Diagnostic) as pe:
            class TestDsl(grammar.Grammar):
                grammar = """
                    not_finished_bnf = [ @dir(12"""
                entry = "not_finished_bnf"
        self.assertEqual(pe.exception.logs[0].msg, "Expected ')'",
                         "failed to get the correct message")
        self.assertEqual(pe.exception.logs[0].location.col, 49,
                         "failed to get the correct position")

    def test_09_parse_error_dsl(self):
        """
        Test parser error in the DSL
        """
        with self.assertRaises(error.Diagnostic) as pe:
            class TestDsl(grammar.Grammar):
                grammar = """
                    not_finished_bnf =[ #hook(12,"""
                entry = "not_finished_bnf"
        self.assertEqual(pe.exception.logs[0].msg, "Expected parameter",
                         "failed to get the correct message")
        self.assertEqual(pe.exception.logs[0].location.col, 50,
                         "failed to get the correct position")

    def test_10_parse_error_dsl(self):
        """
        Test parser error in the DSL
        """
        with self.assertRaises(error.Diagnostic) as pe:
            class TestDsl(grammar.Grammar):
                grammar = """
                    not_finished_bnf =[ #hook("""
                entry = "not_finished_bnf"
        self.assertEqual(pe.exception.logs[0].msg, "Expected parameter",
                         "failed to get the correct message")
        self.assertEqual(pe.exception.logs[0].location.col, 47,
                         "failed to get the correct position")

    def test_11_parse_error_dsl(self):
        """
        Test parser error in the DSL
        """
        with self.assertRaises(error.Diagnostic) as pe:
            class TestDsl(grammar.Grammar):
                grammar = """
                    not_finished_bnf =[ @dir(12,"""
                entry = "not_finished_bnf"
        self.assertEqual(pe.exception.logs[0].msg, "Expected parameter",
                         "failed to get the correct message")
        self.assertEqual(pe.exception.logs[0].location.col, 49,
                         "failed to get the correct position")

    def test_12_parse_error_dsl(self):
        """
        Test parser error in the DSL
        """
        with self.assertRaises(error.Diagnostic) as pe:
            class TestDsl(grammar.Grammar):
                grammar = """
                    not_finished_bnf =[ @dir("""
                entry = "not_finished_bnf"
        self.assertEqual(pe.exception.logs[0].msg, "Expected parameter",
                         "failed to get the correct message")
        self.assertEqual(pe.exception.logs[0].location.col, 46,
                         "failed to get the correct position")

    def test_13_parse_error_dsl(self):
        """
        Test parser error in the DSL
        """
        with self.assertRaises(error.Diagnostic) as pe:
            class TestDsl(grammar.Grammar):
                grammar = """
                    not_finished_bnf =[ [a"""
                entry = "not_finished_bnf"
        self.assertEqual(pe.exception.logs[0].msg, "Expected ']'",
                         "failed to get the correct message")
        self.assertEqual(pe.exception.logs[0].location.col, 43,
                         "failed to get the correct position")

    def test_14_parse_error_dsl(self):
        """
        Test parser error in the DSL
        """
        with self.assertRaises(error.Diagnostic) as pe:
            class TestDsl(grammar.Grammar):
                grammar = """
                    not_finished_bnf =[ ["""
                entry = "not_finished_bnf"
        self.assertEqual(pe.exception.logs[0].msg, "Expected sequences",
                         "failed to get the correct message")
        self.assertEqual(pe.exception.logs[0].location.col, 42,
                         "failed to get the correct position")

    def test_15_ignore_cpp(self):
        """
        Test ignore directive for C/C++
        """
        @meta.hook(DummyCpp)
        def add(self, ast, i):
            ast.last = self.value(i)
            return True
        cxx = DummyCpp()
        res = cxx.parse("""
            a b c /* comment */
            // another comment
            d e/**/f//
            g
        """)
        self.assertTrue(res, "failed to parse dummyCpp")
        self.assertEqual(res.last, 'g', "failed to parse comments")
