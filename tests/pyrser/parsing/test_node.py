import unittest

from pyrser import parsing


class TestNode(unittest.TestCase):
    def test_it_is_true_when_initialized_with_true(self):
        node = parsing.Node(True)
        self.assertTrue(node)

    def test_it_is_false_when_initialized_with_false(self):
        node = parsing.Node(False)
        self.assertFalse(node)

    def test_it_is_true_when_initialized_with_true_node(self):
        node = parsing.Node(parsing.Node(True))
        self.assertTrue(node)

    def test_it_is_false_when_initialized_with_false_node(self):
        node = parsing.Node(parsing.Node(False))
        self.assertFalse(node)

    def test_it_raises_typeerror_when_initialized_with_badtype(self):
        with self.assertRaises(TypeError):
            parsing.Node(0)
