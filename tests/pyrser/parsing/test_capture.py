import unittest
from unittest import mock

from pyrser import parsing


#TODO(bps): finish testing
class TestCapture(unittest.TestCase):
    #TODO(bps): Find what the hell is going on here?
    def test_it_returns_captured_text(self):
        parser = parsing.Parser('captured text')
        clause = parsing.Call(parser.readText, 'captured text')
        capture = parsing.Capture('tagname', clause)
        self.assertEqual(capture(parser), "captured text")
    #test_it_is_false_when_begintag_is_false
    #test_it_is_false_when_clause_is_false
    #test_it_is_false_when_undoIgnore_is_false
    #test_it_is_false_when_endtag_is_false

    def test_it_raises_typeerror_if_tagname_is_not_a_str(self):
        tagname, clause = None, None
        with self.assertRaises(TypeError):
            parsing.Capture(tagname, clause)

    def test_it_raises_typeerror_with_an_empty_tagname(self):
        clause = None
        with self.assertRaises(TypeError):
            parsing.Capture('', clause)
