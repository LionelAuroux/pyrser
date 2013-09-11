import unittest
from unittest import mock

from pyrser import parsing


class TestRule(unittest.TestCase):
    def test_it_evaluate_the_rule(self):
        rulename = 'rule'
        parser = mock.Mock(spec=parsing.BasicParser)
        rule = parsing.Rule(rulename)
        rule(parser)
        parser.eval_rule.assert_called_once_with(rulename)

    def test_it_is_true_when_the_rule_is_true(self):
        parser = mock.Mock(spec=parsing.BasicParser)
        parser.eval_rule.return_value = True
        rule = parsing.Rule('rule')
        self.assertTrue(rule(parser))

    def test_it_is_false_when_the_rule_is_false(self):
        parser = mock.Mock(spec=parsing.BasicParser)
        parser.eval_rule.return_value = False
        rule = parsing.Rule('rule')
        self.assertFalse(rule(parser))
