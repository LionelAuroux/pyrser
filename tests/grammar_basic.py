from collections import ChainMap
import unittest

import pyrser
from pyrser import Grammar, meta, parsing

import weakref
from pyrser.passes import dumpParseTree


# directive must be declare before class definition
@meta.directive("ignore")
class Ignore(parsing.DirectiveWrapper):
    def begin(self, parser, convention: str):
        if convention == "null":
            parser.push_ignore(parsing.Parser.ignore_null)
        return True

    def end(self, parser, convention: str):
        parser.pop_ignore()
        return True


class WordList(Grammar):
    grammar = """
        wordlist ::= [word : w #add_to(_, w)]+ eof
        ;

        word ::= @ignore("null") ['a'..'z'|'A'..'Z']+
        ;
    """
    entry = "wordlist"


class CSV(Grammar):
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


class CSV2(Grammar, CSV):
    entry = "csv2"
    # copy the result of CSV.csv as result of csv2
    grammar = """
        csv2 ::= CSV.csv:_
        ;

        item ::= [CSV.item]?:_
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
        print("PARSE TREE :%s" % ws.dumpParseTree())
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
