import unittest
from unittest import mock

from pyrser import parsing


class TestLookAhead(unittest.TestCase):
    def test_it_is_true_when_clause_is_false(self):
        clause = mock.Mock(return_value=False)
        looka = parsing.LookAhead(clause)
        parser = mock.Mock(**{'read_eof.return_value': False})
        self.assertTrue(looka(parser))
        parser._stream.save_context.assert_called_once_with()
        parser._stream.restore_context.assert_called_once_with()

    def test_it_is_false_when_clause_is_true(self):
        clause = mock.Mock(return_value=True)
        looka = parsing.LookAhead(clause)
        parser = mock.Mock(**{'read_eof.return_value': False})
        self.assertFalse(looka(parser))
        parser._stream.save_context.assert_called_once_with()
        parser._stream.restore_context.assert_called_once_with()
