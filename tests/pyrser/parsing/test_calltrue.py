import unittest
from unittest import mock

from pyrser.parsing import CallTrue


class TestCallTrue(unittest.TestCase):
    def test_it_calls_its_clause_with_given_args(self):
        clause, args = mock.Mock(), (1, 2, 3)
        call = CallTrue(clause, *args)
        call()
        clause.assert_called_once_with(*args)

    def test_it_returns_true_when_clause_is_true(self):
        clause = mock.Mock(return_value=True)
        call = CallTrue(clause)
        self.assertTrue(call())

    def test_it_returns_true_when_clause_is_false(self):
        clause = mock.Mock(return_value=False)
        call = CallTrue(clause)
        self.assertTrue(call())
