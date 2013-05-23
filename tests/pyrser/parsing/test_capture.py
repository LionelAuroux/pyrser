import collections
import unittest
from unittest import mock

from pyrser import parsing


class TestCapture(unittest.TestCase):
    def test_it_returns_clause_result(self):
        res = mock.Mock()
        # if __len__ == 0, bool(res) is False
        # overrides with __bool__
        res.__len__ = lambda x: 0
        res.__bool__ = lambda x: True
        parser = mock.Mock(rulenodes=collections.ChainMap(),
                           **{'begin_tag.return_value': True})
        clause = mock.Mock(return_value=res)
        capture = parsing.Capture('tagname', clause)
        self.assertIs(capture(parser), res)
        clause.assert_called_once_with(parser)

    def test_it_wraps_boolean_result_in_node(self):
        res = mock.Mock()
        parser = mock.Mock(rulenodes=collections.ChainMap(),
                           **{'get_tag.return_value': res})
        clause = mock.Mock(return_value=True)
        capture = parsing.Capture('tagname', clause)
        expected_res = parsing.Node(True)
        expected_res.value = res
        self.assertEqual(capture(parser), expected_res)
        clause.assert_called_once_with(parser)

    def test_it_is_false_when_begintag_is_false(self):
        parser = mock.Mock(**{'begin_tag.return_value': False})
        capture = parsing.Capture('tagname', None)
        self.assertFalse(capture(parser))
        parser.begin_tag.assert_called_once_with('tagname')

    def test_it_is_false_when_clause_is_false(self):
        parser = mock.Mock(rulenodes=collections.ChainMap(),
                           **{'begin_tag.return_value': True})
        clause = mock.Mock(return_value=False)
        capture = parsing.Capture('tagname', clause)
        self.assertFalse(capture(parser))
        clause.assert_called_once_with(parser)

    @unittest.skip('fix it')
    def test_it_is_false_when_undoIgnore_is_false(self):
        parser = mock.Mock(rulenodes={},
                           **{'begin_tag.return_value': True,
                              'undo_ignore.return_value': False})
        clause = mock.Mock(return_value=True)
        capture = parsing.Capture('tagname', clause)
        self.assertFalse(capture(parser))

    def test_it_is_false_when_endtag_is_false(self):
        parser = mock.Mock(rulenodes=collections.ChainMap(),
                           **{'begin_tag.return_value': True,
                              'undo_ignore.return_value': True,
                              'end_tag.return_value': False})
        clause = mock.Mock(return_value=True)
        capture = parsing.Capture('tagname', clause)
        self.assertFalse(capture(parser))

    def test_it_raises_typeerror_if_tagname_is_not_a_str(self):
        tagname, clause = None, None
        with self.assertRaises(TypeError):
            parsing.Capture(tagname, clause)

    def test_it_raises_typeerror_with_an_empty_tagname(self):
        clause = None
        with self.assertRaises(TypeError):
            parsing.Capture('', clause)
