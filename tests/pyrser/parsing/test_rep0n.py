import unittest
from unittest import mock

from pyrser import parsing


class TestRep0N(unittest.TestCase):
    def test_it_calls_skipIgnore_before_calling_clause(self):
        parser = mock.Mock(spec=parsing.BasicParser)
        clause = mock.Mock(side_effect=[True, False])
        parser.clause = clause
        parsing.Rep0N(clause)(parser)
        self.assertEqual(
            [mock.call.skip_ignore(), mock.call.clause(parser)] * 2,
            parser.method_calls)

    def test_it_calls_clause_as_long_as_clause_is_true(self):
        parser = mock.Mock(spec=parsing.BasicParser)
        clause = mock.Mock(side_effect=[True, True, False])
        rep = parsing.Rep0N(clause)
        rep(parser)
        self.assertEqual(3, clause.call_count)

    def test_it_is_true_when_clause_is_false(self):
        parser = mock.Mock(spec=parsing.BasicParser)
        clause = mock.Mock(return_value=False)
        parser.clause = clause
        rep = parsing.Rep0N(clause)
        self.assertTrue(rep(parser))
