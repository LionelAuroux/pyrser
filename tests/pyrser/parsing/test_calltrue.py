import unittest
from unittest import mock

from pyrser import parsing


class TestCallTrue(unittest.TestCase):
    def test_it_calls_its_clause_with_given_args(self):
        parser, clause, args = mock.Mock(), mock.Mock(), (1, 2, 3)
        call = parsing.CallTrue(clause, *args)
        call(parser)
        clause.assert_called_once_with(*args)

    def test_it_returns_true_when_clause_is_true(self):
        parser = mock.Mock()
        clause = mock.Mock(return_value=True)
        call = parsing.CallTrue(clause)
        self.assertTrue(call(parser))

    def test_it_returns_true_when_clause_is_false(self):
        parser = mock.Mock()
        clause = mock.Mock(return_value=False)
        call = parsing.CallTrue(clause)
        self.assertTrue(call(parser))
