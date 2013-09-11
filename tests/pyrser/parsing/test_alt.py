import unittest
from unittest import mock

from pyrser import parsing


class TestAlt(unittest.TestCase):
    def test_it_calls_skipIgnore_before_each_clause(self):
        parser = mock.Mock(spec=parsing.BasicParser)
        pt = mock.Mock(return_value=False)
        parser.pt = pt
        parsing.Alt(pt, pt)(parser)
        calls = list(filter(lambda x: x in (mock.call.skip_ignore(),
                                            mock.call.pt(parser)),
                     parser.method_calls))
        self.assertEqual(
            calls,
            [mock.call.skip_ignore(), mock.call.pt(parser)] * 2)

    def test_it_save_current_context_before_each_clause(self):
        parser = mock.Mock(spec=parsing.BasicParser)
        pt = mock.Mock(return_value=False)
        parser.pt = pt
        parsing.Alt(pt, pt)(parser)
        calls = list(filter(lambda x: x in (mock.call._stream.save_context(),
                                            mock.call.pt(parser)),
                     parser.method_calls))
        self.assertEqual(
            calls,
            [mock.call._stream.save_context(), mock.call.pt(parser)] * 2)

    def test_it_validate_context_if_clause_is_true(self):
        parser = mock.Mock(spec=parsing.BasicParser)
        pt = mock.Mock(return_value=True)
        parsing.Alt(pt)(parser)
        self.assertTrue(parser._stream.validate_context.called)

    def test_it_restore_saved_context_if_clause_is_false(self):
        parser = mock.Mock(spec=parsing.BasicParser)
        pt = mock.Mock(return_value=False)
        parsing.Alt(pt)(parser)
        self.assertTrue(parser._stream.restore_context.called)

    def test_it_calls_all_clauses_in_order_if_they_all_false(self):
        parser = mock.Mock(spec=parsing.BasicParser)
        clauses = mock.Mock(**{'pt0.return_value': False,
                               'pt1.return_value': False})
        parsing.Alt(clauses.pt0, clauses.pt1)(parser)
        self.assertEqual([mock.call.pt0(parser), mock.call.pt1(parser)],
                         clauses.mock_calls)

    def test_it_stops_calling_clauses_if_a_clause_is_true(self):
        parser = mock.Mock(spec=parsing.BasicParser)
        clauses = mock.Mock(**{'clause0.return_value': True,
                               'clause1.return_value': False})
        parsing.Alt(clauses.pt0, clauses.pt1)(parser)
        self.assertEqual([mock.call.pt0(parser)], clauses.mock_calls)

    def test_it_is_true_if_a_clause_is_true(self):
        parser = mock.Mock(spec=parsing.BasicParser)
        pt = mock.Mock(return_value=True)
        alt = parsing.Alt(pt)
        self.assertTrue(alt(parser))

    def test_it_is_false_if_all_clauses_are_false(self):
        parser = mock.Mock(spec=parsing.BasicParser)
        clause0 = mock.Mock(return_value=False)
        clause1 = mock.Mock(return_value=False)
        alt = parsing.Alt(clause0, clause1)
        self.assertFalse(alt(parser))
