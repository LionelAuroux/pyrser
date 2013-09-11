import unittest
from unittest import mock

from pyrser import parsing


class TestNegation(unittest.TestCase):
    def test_it_is_false_when_clause_is_true(self):
        clause = mock.Mock(return_value=True)
        neg = parsing.Neg(clause)
        parser = mock.Mock(**{'_stream.restore_context.return_value': False})
        self.assertFalse(neg(parser))
        parser._stream.save_context.assert_called_once_with()
        parser._stream.restore_context.assert_called_once_with()

    def test_it_is_true_when_clause_is_false(self):
        clause = mock.Mock(return_value=False)
        neg = parsing.Neg(clause)
        parser = mock.Mock()
        self.assertTrue(neg(parser))
        parser._stream.save_context.assert_called_once_with()
        parser._stream.validate_context.assert_called_once_with()
