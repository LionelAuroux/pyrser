import unittest
from unittest import mock

from pyrser import parsing


class TestRepOptional(unittest.TestCase):
    def test_it_calls_skipIgnore_before_clause(self):
        parser = mock.Mock(spec=parsing.BasicParser)
        clause = mock.Mock(return_value=True)
        parser.clause = clause
        parsing.RepOptional(clause)(parser)
        self.assertEqual(
            [mock.call.skip_ignore(), mock.call.clause(parser)],
            parser.method_calls)

    def test_it_is_true_when_clause_is_true(self):
        parser = mock.Mock(spec=parsing.BasicParser)
        clause = mock.Mock(return_value=True)
        rep = parsing.RepOptional(clause)
        self.assertTrue(rep(parser))

    def test_it_is_true_when_clause_is_false(self):
        parser = mock.Mock(spec=parsing.BasicParser)
        clause = mock.Mock(return_value=False)
        rep = parsing.RepOptional(clause)
        self.assertTrue(rep(parser))
