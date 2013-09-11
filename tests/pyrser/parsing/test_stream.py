import unittest

from pyrser import parsing
from pyrser.parsing.parserStream import Position


class TestParserStream(unittest.TestCase):
    def test_its_len_is_its_content_len(self):
        content = "some content"
        stream = parsing.Stream(content)
        self.assertEqual(len(content), len(stream))

    def test_its_content_can_be_accessed_like_a_string(self):
        content = "some content"
        stream = parsing.Stream(content)
        self.assertEqual(content[5], stream[5])
        self.assertEqual(content[2:], stream[2:])

    def test_it_increments_position(self):
        stream = parsing.Stream(" ")
        prev_pos = stream.index
        stream.incpos()
        self.assertLess(prev_pos, stream.index)

    def test_it_increments_position_on_newline(self):
        stream = parsing.Stream("\n")
        prev_line = stream.lineno
        stream.incpos()
        self.assertEqual(1, stream.col_offset)
        self.assertLess(prev_line, stream.lineno)

    def test_it_does_not_increment_position_passed_eof(self):
        stream = parsing.Stream("")
        pos = stream.index
        stream.incpos()
        self.assertEqual(pos, stream.index)

    def test_it_decrements_position(self):
        stream = parsing.Stream("a")
        stream._cursor.step_next_char()
        stream.decpos()
        self.assertEqual(0, stream.index)

    def test_it_decrements_position_on_newline(self):
        stream = parsing.Stream("\n")
        stream._cursor.step_next_line()
        stream._cursor.step_next_char()
        stream.decpos()
        self.assertEqual(1, stream.lineno)

    def test_it_does_not_decrement_position_before_bof(self):
        stream = parsing.Stream("")
        stream.decpos()
        self.assertEqual(0, stream.index)

    def test_it_saves_context(self):
        stream = parsing.Stream()
        contexts = stream._contexts
        nb_ctx = len(contexts)
        stream.save_context()
        self.assertEqual(nb_ctx + 1, len(contexts))

    def test_it_restore_context(self):
        stream = parsing.Stream()
        pos = Position(42, 0, 0)
        stream._contexts.insert(0, pos)
        stream.restore_context()
        self.assertEqual(pos.index, stream.index)

    def test_it_validates_context(self):
        stream = parsing.Stream()
        stream._contexts.insert(0, Position(42, 0, 0))
        stream.validate_context()
        self.assertEqual(0, stream.index)
