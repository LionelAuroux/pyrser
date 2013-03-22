import unittest

from pyrser import parsing


class TestBasicParser(unittest.TestCase):
    def test_it_is_true_when_peeked_text_is_equal(self):
        parser = parsing.BasicParser("Some text to read.")
        self.assertTrue(parser.peekText("Some text"))

    def test_it_is_false_when_peeked_text_is_different(self):
        parser = parsing.BasicParser("Not some text to read.")
        self.assertFalse(parser.peekText("some text"))

    def test_it_can_not_read_text_after_eof(self):
        parser = parsing.BasicParser("")
        self.assertFalse(parser.readText("no read"))

# Streams
# Define stream stacking behavior in accord to reading
# readChar
# readRange
# readText

#Maybe
# readUntil
# readUntilEOF

#Move
# Ignores
# Tags (capture)
# RuleNodes (rule result)
# Rules
# Hooks
