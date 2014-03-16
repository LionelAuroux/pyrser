import unittest
from pyrser import grammar
from pyrser import meta
from pyrser import parsing
from pyrser import error
from pyrser.directives import *


class IgnoreNull(grammar.Grammar):
    grammar = """
        root =[ @ignore("null") [ item : i #add_to(_, i) ]+ eof ]

        item = [ ' ' | 'a'..'z' | 'A'..'Z' | '\n' | '\t' | '\v' | '.' ]
    """
    entry = "root"


class IgnoreBlanks(grammar.Grammar):
    grammar = """
        root =[ @ignore("blank") [ [ item : i #add_to(_, i) ]+ eof ] ]

        item = [
            'a'..'z' | 'A'..'Z' | '.' | '!' |
            ' ' | '\n' | '\r' | '\t' | '\v' | '\f' | '\b'
        ]
    """
    entry = "root"


class IgnoreCPP(grammar.Grammar):
    grammar = """
        root =[ @ignore("C/C++") [ #init(_) [ word:w #add_to(_, w) ]* eof ] ]

        word = [ @ignore("null") ['a'..'z'|'A'..'Z']+ ]
    """
    entry = "root"


class GrammarDirective_Test(unittest.TestCase):
    def test_01_ignore_null(self):
        """
        Test @ignore("null") directive
        """
        @meta.hook(IgnoreNull)
        def add_to(self, mylist, item):
            if not hasattr(mylist, 'lst'):
                mylist.lst = [self.value(item)]
            else:
                mylist.lst.append(self.value(item))
            return True

        source = "a\nb\tc d\vF."
        l = IgnoreNull(source)
        res = l.parse()
        self.assertTrue(res, "Failed to parse IgnoreNull")
        self.assertEqual(len(res.lst), len(source),
                         "failed to retrieve {} tokens".format(len(source)))

    def test_02_ignore_blank(self):
        """
        Test @ignore("blank") directive
        """
        @meta.hook(IgnoreBlanks)
        def add_to(self, mylist, item):
            if not hasattr(mylist, 'lst'):
                mylist.lst = [self.value(item)]
            else:
                mylist.lst.append(self.value(item))
            return True

        source = "a\nb\tc d\vF\f.\r!\b"
        l = IgnoreBlanks(source)
        res = l.parse()
        self.assertTrue(res, "Failed to parse IgnoreBlanks")
        self.assertEqual(len(res.lst), 8, "failed to retrieve 8 tokens")
        self.assertEqual(res.lst[6], "!", "Failed to reach lst[6]")

    def test_03_ignore_cpp(self):
        """
        Test @ignore("C/C++") directive
        """
        @meta.hook(IgnoreCPP)
        def init(self, mylist):
            mylist.lst = []
            return True

        @meta.hook(IgnoreCPP)
        def add_to(self, mylist, item):
            mylist.lst.append(self.value(item))
            return True

        source = """/* Only enclosed */"""
        expected = []
        l = IgnoreCPP(source)
        res = l.parse()
        self.assertTrue(res, "Failed to parse CPP enclosed-comment only")
        self.assertEqual(len(res.lst), len(expected),
                         "Found tokens when none expected")
        self.assertEqual(res.lst, expected,
                         "Result didn't match expected result")

    def test_04_ignore_cpp(self):
        """
        Test @ignore("C/C++") directive
        """
        @meta.hook(IgnoreCPP)
        def init(self, mylist):
            mylist.lst = []
            return True

        @meta.hook(IgnoreCPP)
        def add_to(self, mylist, item):
            mylist.lst.append(self.value(item))
            return True

        source = """// Only double slash """
        expected = []
        l = IgnoreCPP(source)
        res = l.parse()
        self.assertTrue(res, "Failed to parse CPP double-slash comment only")
        self.assertEqual(len(res.lst), len(expected),
                         "Found tokens when none expected")
        self.assertEqual(res.lst, expected,
                         "Result didn't match expected result")

    def test_05_ignore_cpp(self):
        """
        Test @ignore("C/C++") directive
        """
        @meta.hook(IgnoreCPP)
        def init(self, mylist):
            mylist.lst = []
            return True

        @meta.hook(IgnoreCPP)
        def add_to(self, mylist, item):
            mylist.lst.append(self.value(item))
            return True

        source = """
        /*
         * This is
         * a simple
         * multiline comment
         */
         """
        expected = []
        l = IgnoreCPP(source)
        res = l.parse()
        self.assertTrue(res, "Failed to parse CPP multi-line comment only")
        self.assertEqual(len(res.lst), len(expected),
                         "Found tokens when none expected")
        self.assertEqual(res.lst, expected,
                         "Result didn't match expected result")

    def test_08_ignore_cpp(self):
        """
        Test @ignore("C/C++") directive
        """
        @meta.hook(IgnoreCPP)
        def init(self, mylist):
            mylist.lst = []
            return True

        @meta.hook(IgnoreCPP)
        def add_to(self, mylist, item):
            mylist.lst.append(self.value(item))
            return True

        source = """
            int pouet paf /* inline comment */ pouf
            int pouet paf pouf //end comment
            paf/* int pouet */pouf
            int pouet/*paf*/pouf
            //test qui /* pouet paf */
            // Test
            int/*
             * Multi-line
             * comment
             */test
            test end
            /*last comment for the road*/"""
        expected = ["int", "pouet", "paf", "pouf",
                    "int", "pouet", "paf", "pouf",
                    "paf", "pouf",
                    "int", "pouet", "pouf",
                    "int",
                    "test",
                    "test", "end"]
        l = IgnoreCPP(source)
        res = l.parse()
        self.assertTrue(res, "Failed to parse IgnoreBlanks")
        self.assertEqual(len(res.lst), len(expected),
                         "failed to retrieve {} tokens".format(len(expected)))
        self.assertEqual(res.lst, expected,
                         "Result didn't match expected result")
