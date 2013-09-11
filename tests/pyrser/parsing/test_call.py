import unittest
from unittest import mock

from pyrser import parsing


class TestCall(unittest.TestCase):
    def test_it_calls_its_clause_with_given_args(self):
        parser, clause, args = mock.Mock(), mock.Mock(), (1, 2, 3)
        parsing.Call(clause, *args)(parser)
        clause.assert_called_once_with(parser, *args)

    def test_it_calls_its_method_clause_with_given_args(self):
        import types
        clause = mock.Mock(spec=types.MethodType)
        parser, args = mock.Mock(), (1, 2, 3)
        parsing.Call(clause, *args)(parser)
        clause.assert_called_once_with(parser, *args)

    def test_it_returns_true_when_clause_is_true(self):
        parser = mock.Mock()
        clause = mock.Mock(return_value=True)
        call = parsing.Call(clause)
        self.assertTrue(call(parser))

    def test_it_returns_false_when_clause_is_false(self):
        parser = mock.Mock()
        clause = mock.Mock(return_value=False)
        call = parsing.Call(clause)
        self.assertFalse(call(parser))
