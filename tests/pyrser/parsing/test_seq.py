import unittest
from unittest import mock

from pyrser import parsing


class TestSeq(unittest.TestCase):
    def test_it_calls_skipIgnore_before_each_clause(self):
        parser = mock.Mock(spec=parsing.BasicParser)
        clause = mock.Mock(return_value=True)
        parser.clause = clause
        parsing.Seq(clause, clause)(parser)
        self.assertEqual(
            [mock.call.skip_ignore(), mock.call.clause(parser)] * 2,
            parser.mock_calls)

    def test_it_calls_all_clauses_in_order_if_each_clause_is_true(self):
        parser = mock.Mock(spec=parsing.BasicParser)
        clauses = mock.Mock(**{'clause0.return_value': True,
                               'clause1.return_value': True})
        parsing.Seq(clauses.clause0, clauses.clause1)(parser)
        self.assertEqual(
            [mock.call.clause0(parser), mock.call.clause1(parser)],
            clauses.mock_calls)

    def test_it_stops_calling_clauses_if_a_clause_is_false(self):
        parser = mock.Mock(spec=parsing.BasicParser)
        clauses = mock.Mock(**{'clause0.return_value': False,
                               'clause1.return_value': True})
        parsing.Seq(clauses.clause0, clauses.clause1)(parser)
        self.assertEqual([mock.call.clause0(parser)], clauses.mock_calls)

    def test_it_is_true_if_all_clauses_are_true(self):
        parser = mock.Mock(spec=parsing.BasicParser)
        clause = mock.Mock(return_value=True)
        clauses = parsing.Seq(clause, clause)
        self.assertTrue(clauses(parser))

    def test_is_is_false_if_any_clause_is_false(self):
        parser = mock.Mock(spec=parsing.BasicParser)
        clause0 = mock.Mock(return_value=True)
        clause1 = mock.Mock(return_value=False)
        clauses = parsing.Seq(clause0, clause1)
        self.assertFalse(clauses(parser))

    def test_it_raises_typeerror_with_no_clause(self):
        with self.assertRaises(TypeError):
            parsing.Seq()
