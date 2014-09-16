from pyrser import meta, parsing


@meta.rule(parsing.Parser, "Base.ignore_cxx")
def ignore_cxx(self) -> bool:
    """Consume comments and whitespace characters."""
    self._stream.save_context()
    while not self.read_eof():
        idxref = self._stream.index
        if self._stream.peek_char in " \t\v\f\r\n":
            while (not self.read_eof()
                    and self._stream.peek_char in " \t\v\f\r\n"):
                self._stream.incpos()
        if self.peek_text("//"):
            while not self.read_eof() and not self.peek_char("\n"):
                self._stream.incpos()
            if not self.read_char("\n") and self.read_eof():
                return self._stream.validate_context()
        if self.peek_text("/*"):
            while not self.read_eof() and not self.peek_text("*/"):
                self._stream.incpos()
            if not self.read_text("*/") and self.read_eof():
                return self._stream.restore_context()
        if idxref == self._stream.index:
            break
    return self._stream.validate_context()


@meta.directive("ignore")
class Ignore(parsing.DirectiveWrapper):
    def begin(self, parser, convention: str):
        if convention == "null":
            parser.push_ignore(parsing.Parser.ignore_null)
        if convention == "C/C++":
            parser.push_ignore(parsing.Parser.ignore_cxx)
        if convention == "blanks":
            parser.push_ignore(parsing.Parser.ignore_blanks)
        return True

    def end(self, parser, convention: str):
        parser.pop_ignore()
        return True
