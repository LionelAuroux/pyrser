import unittest
from unittest import mock

from pyrser import parsing


class TestRep1N(unittest.TestCase):
    def test_it_calls_skipIgnore_before_calling_clause(self):
        parser = mock.Mock(spec=parsing.BasicParser)
        clause = mock.Mock(side_effect=[True, False])
        parser.clause = clause
        rep = parsing.Rep1N(clause)
        rep(parser)
        self.assertEqual(
            [mock.call.skip_ignore(), mock.call.clause(parser)] * 2,
            parser.method_calls)

    def test_it_calls_clause_as_long_as_clause_is_true(self):
        parser = mock.Mock(spec=parsing.BasicParser)
        clause = mock.Mock(side_effect=[True, True, False])
        rep = parsing.Rep1N(clause)
        rep(parser)
        self.assertEqual(3, clause.call_count)

    def test_it_is_true_when_clause_is_true_once(self):
        parser = mock.Mock(spec=parsing.BasicParser)
        clause = mock.Mock(side_effect=[True, False])
        rep = parsing.Rep1N(clause)
        self.assertTrue(rep(parser))

    def test_it_is_true_when_clause_is_true_more_than_once(self):
        parser = mock.Mock(spec=parsing.BasicParser)
        clause = mock.Mock(side_effect=[True, True, True, False])
        rep = parsing.Rep1N(clause)
        self.assertTrue(rep(parser))

    def test_it_is_false_when_clause_is_false(self):
        parser = mock.Mock(spec=parsing.BasicParser)
        clause = mock.Mock(return_value=False)
        rep = parsing.Rep1N(clause)
        self.assertFalse(rep(parser))
