import unittest
from unittest import mock

from pyrser import parsing


class TestComplement(unittest.TestCase):
    def test_it_is_true_when_clause_is_false(self):
        clause = mock.Mock(return_value=False)
        comp = parsing.Complement(clause)
        parser = mock.Mock(**{'read_eof.return_value': False})
        self.assertTrue(comp(parser))

    def test_it_is_false_when_clause_is_true(self):
        clause = mock.Mock(return_value=True)
        comp = parsing.Complement(clause)
        parser = mock.Mock(**{'read_eof.return_value': False})
        self.assertFalse(comp(parser))
