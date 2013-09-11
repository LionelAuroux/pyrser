# error handling


#forward declaration of BasicParser
class BasicParser:
    pass


class ParseError(Exception):
    def __init__(self, message, stream_name="", pos=None, line="", **kwargs):
        msg = (message + " in {stream_name} at line {line} col {col}\n"
               "{last_read_line}\n"
               "{underline}")
        underline = "%s^" % ('-' * (pos.col_offset - 1))
        kwargs.update(
            message=message, stream_name=stream_name,
            line=pos.lineno, col=pos.col_offset,
            last_read_line=line, underline=underline)
        self.raw_msg = message
        self.msg = msg.format(**kwargs)
        Exception.__init__(self, self.msg)
        self.stream_name = stream_name
        self.error_position = pos
        self.error_line = line


def throw(msg: str, parser: BasicParser, **kw):
    """Convenient function to raise a ParseError"""
    kw.update(
        stream_name=parser._stream.name,
        pos=parser._stream._cursor.max_readed_position,
        line=parser._stream.last_readed_line)
    raise ParseError(msg, **kw)
