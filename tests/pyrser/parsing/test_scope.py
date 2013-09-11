import unittest
from unittest import mock

from pyrser import parsing


class TestScope(unittest.TestCase):
    def test_it_returns_the_clause_result_when_all_clauses_are_true(self):
        parser = parsing.BasicParser()
        begin_end = mock.Mock(return_value=True)
        clause = mock.Mock(return_value=mock.sentinel.clause)
        scope = parsing.Scope(begin_end, begin_end, clause)
        self.assertEqual(scope(parser), mock.sentinel.clause)

    def test_it_is_false_when_begin_clause_is_false(self):
        parser = parsing.BasicParser()
        begin = mock.Mock(return_value=False)
        clause = mock.Mock(return_value=True)
        scope = parsing.Scope(begin, clause, clause)
        self.assertFalse(scope(parser))

    def test_it_is_false_when_clause_is_false(self):
        parser = parsing.BasicParser()
        begin_end = mock.Mock(return_value=True)
        clause = mock.Mock(return_value=False)
        scope = parsing.Scope(begin_end, begin_end, clause)
        self.assertFalse(scope(parser))

    def test_it_is_false_when_end_clause_is_false(self):
        parser = parsing.BasicParser()
        clause = mock.Mock(return_value=True)
        end = mock.Mock(return_value=False)
        scope = parsing.Scope(clause, end, clause)
        self.assertFalse(scope(parser))
