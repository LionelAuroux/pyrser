import unittest
from unittest import mock

from pyrser import parsing


class TestCapture(unittest.TestCase):
    #TODO(bps): Find what the hell is going on here?
    @unittest.skip
    def test_it_returns_captured_text(self):
        parser = BasicParser('captured text')
        clause = Call(parser.readText, 'captured text')
        capture = parsing.Capture(parser, 'tagname', clause)
        self.assertEqual(capture(), "captured text")

    def test_it_raises_typeerror_if_tagname_is_not_a_str(self):
        parser = None
        clause = mock.Mock()
        with self.assertRaises(TypeError):
            parsing.Capture(parser, None, clause)

    def test_it_raises_typeerror_with_an_empty_tagname(self):
        parser = None
        clause = mock.Mock()
        with self.assertRaises(TypeError):
            parsing.Capture(parser, '', clause)
