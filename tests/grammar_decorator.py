import unittest
import tempfile
import os

from pyrser import grammar
from pyrser import meta
from pyrser import parsing
from pyrser import error
from pyrser.directives import Trace


class TraceSimple(grammar.Grammar):
    grammar = """
        root = [ @ignore("null") @trace("logfile")
                [ space | ponctuation | word ]+ eof
            ]

        space = [ ' ' ]

        word = [ 'This' | 'is' | 'a' | 'warning' ]

        ponctuation = [ '!' | '.' | '?' ]

    """
    entry = "root"


class GrammarDecorator_Test(unittest.TestCase):
    def test_01_trace_failure(self):
        """
        Test @trace decorator directive
        """
        source = "word"
        l = TraceSimple(source)
        res = l.parse()

        trace = ""
        with open("logfile") as flog:
            trace = flog.read()
        os.remove("logfile")

        self.assertFalse(res, "Did not fail to parse TraceSimple")
        self.assertEqual(trace,
                         "[space] Entering\n"
                         + "[space] Failed\n"
                         + "[ponctuation] Entering\n"
                         + "[ponctuation] Failed\n"
                         + "[word] Entering\n"
                         + "[word] Failed\n",
                         "Trace doesn't match expected result.")

    def test_02_trace_success(self):
        """
        Test @trace decorator directive
        """
        source = " "
        l = TraceSimple(source)
        res = l.parse()

        trace = ""
        with open("logfile") as flog:
            trace = flog.read()
        os.remove("logfile")

        self.assertTrue(res, "Failed to parse TraceSimple")
        self.assertEqual(trace,
                         "[space] Entering\n"
                         + "[space] Succeeded\n"
                         + "[space] Entering\n"
                         + "[space] Failed\n"
                         + "[ponctuation] Entering\n"
                         + "[ponctuation] Failed\n"
                         + "[word] Entering\n"
                         + "[word] Failed\n"
                         + "[eof] Entering\n"
                         + "[eof] Succeeded\n",
                         "Trace doesn't match expected result.")
