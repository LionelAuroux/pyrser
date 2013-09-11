import unittest
from unittest import mock

from pyrser import parsing


class TestHook(unittest.TestCase):
    def test_it_evaluates_hook(self):
        hookname, params = 'hook', [(1, int), (2, int), (3, int)]
        parser = mock.Mock(spec=parsing.BasicParser)
        hook = parsing.Hook(hookname, params)
        hook(parser)
        parser.eval_hook.assert_called_once_with(hookname, [1, 2, 3])

    def test_it_is_true_when_the_hook_is_true(self):
        parser = mock.Mock(
            spec=parsing.BasicParser,
            **{'eval_hook.return_value': True})
        hook = parsing.Hook('hook', [])
        self.assertTrue(hook(parser))

    def test_it_is_false_when_the_hook_is_false(self):
        parser = mock.Mock(
            spec=parsing.BasicParser,
            **{'eval_hook.return_value': False})
        hook = parsing.Hook('hook', [])
        self.assertFalse(hook(parser))

    def test_it_evaluates_hook_with_param_values(self):
        parser = mock.Mock(spec=parsing.BasicParser)
        hook = parsing.Hook('hook', [(1, int), ('', str), ([], list)])
        hook(parser)
        parser.eval_hook.assert_called_once_with('hook', [1, '', []])

    def test_it_evaluates_hook_with_weakref_for_node_values(self):
        node = parsing.Node()
        parser = mock.Mock(
            spec=parsing.BasicParser,
            **{'rulenodes': {'hooknode': node}})
        hook = parsing.Hook('hook', [('hooknode', parsing.Node)])
        hook(parser)
        parser.eval_hook.assert_called_once_with('hook', [node])

    def test_it_raises_typeerror_when_param_is_malformed(self):
        with self.assertRaises(TypeError):
            parsing.Hook('hook', [(None, None)])

    def test_it_raises_typeerror_when_param_type_mismatch_value_type(self):
        with self.assertRaises(TypeError):
            hook = parsing.Hook('hook', [(1, str)])
            hook(None)
