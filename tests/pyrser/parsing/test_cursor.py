import unittest

from pyrser.parsing.parserStream import Cursor, Position


class TestCursor(unittest.TestCase):
    def test_it_sets_default_position(self):
        default = Position(0, 1, 1)
        self.assertEqual(default, Cursor().position)

    def test_it_sets_position_to_provided_position(self):
        pos = Position(1, 3, 5)
        self.assertEqual(pos, Cursor(pos).position)

    def test_it_increments_cursor_to_next_char_position(self):
        start, dest = Position(1, 3, 5), Position(1 + 1, 3, 5 + 1)
        cursor = Cursor(start)
        cursor.step_next_char()
        self.assertEqual(dest, cursor.position)

    def test_it_increments_line(self):
        start, dest = Position(1, 3, 5), Position(1, 3 + 1, 0)
        cursor = Cursor(start)
        cursor.step_next_line()
        self.assertEqual(dest, cursor.position)

    def test_it_decrements_cursor_to_prev_char_position(self):
        start, dest = Position(1, 3, 5), Position(1 - 1, 3, 5 - 1)
        cursor = Cursor(start)
        cursor.step_prev_char()
        self.assertEqual(dest, cursor.position)

    def test_it_decrements_line(self):
        pos = Position(1, 3, 5)
        cursor = Cursor(pos)
        cursor.step_next_line()
        cursor.step_prev_line()
        self.assertEqual(pos, cursor.position)
