# error handling
import os
import inspect
import re
from collections import *
from pyrser import meta


#forward declaration of BasicParser
class BasicParser:
    pass


Severity = meta.enum('INFO', 'WARNING', 'ERROR')


class LocationInfo:
    __slots__ = ['filepath', 'line', 'col', 'size']

    def __init__(self, filepath: str, line: int, col: int, size: int=1):
        self.filepath = filepath
        self.line = line
        self.col = col
        self.size = size

    def get_content(self) -> str:
        raise Exception(
            "You can't use LocationInfo directly, use subclasses."
        )


class StreamInfo(LocationInfo):
    """
    Primitive to stream info in all diagnostic.
    """

    def __init__(self, stream: 'Stream'):
        super().__init__(stream.name, stream.lineno, stream.col_offset, 1)
        self.content = stream.last_readed_line + '\n'

    def get_content(self) -> str:
        cl = re.compile('(\s+).')
        m = cl.match(self.content)
        txt = "from {f} at line:{l} col:{c} :\n{content}{i}".format(
            f=self.filepath,
            content=self.content,
            l=self.line,
            c=self.col,
            i=(' ' * (len(m.group(1)))) + '^'
        )
        return txt


class FileInfo(LocationInfo):
    """
    Primitive to handle file info in all diagnostic.
    """
    def __init__(self, filepath: str, line: int, col: int, size: int=1):
        super().__init__(os.path.abspath(filepath), line, col, size)

    def from_current(pos=1):
        f = inspect.currentframe()
        fcaller = inspect.getouterframes(f)[pos]
        cl = re.compile('(\s+).')
        call = fcaller[4][0]
        m = cl.match(call)
        li = FileInfo(fcaller[1], fcaller[2], len(m.group(1)) + 1)
        return li

    def get_content(self) -> str:
        f = open(self.filepath, 'r')
        lines = list(f)
        f.close()
        txtline = lines[self.line - 1]
        indent = ' ' * (self.col - 1)
        if self.size != 1:
            indent += '~' * (self.size)
        else:
            indent += '^'
        txt = "from {f} at line:{l} col:{c} :\n{content}{i}".format(
            f=self.filepath,
            content=txtline,
            l=self.line,
            c=self.col,
            i=indent
        )
        return txt


class Notification:
    """
    Just One notification
    """
    def __init__(self, severity: Severity, msg: str,
                 location: LocationInfo=None):
        self.severity = severity
        self.location = location
        self.msg = msg

    def get_content(self) -> str:
        sevtxt = ""
        locinfos = ""
        if self.location is not None:
            locinfos = self.location.get_content()
        txt = "{s} : {msg}\n{l}".format(
            s=Severity.rmap[self.severity].lower(),
            msg=self.msg,
            l=locinfos
        )
        return txt


class Diagnostic:
    """
    The diagnostic object is use to handle easily
    all errors/warnings/infos in a compiler that you could
    encounter. Error while parsing, Error while type checking etc...
    You could use different severity for your notification.
    """
    def __init__(self):
        self.logs = OrderedDict()

    def notify(self, severity: Severity, msg: str,
               location: object, relatedid=None) -> int:
        nfy = Notification(severity, msg, location)
        idx = id(nfy)
        self.logs[idx] = (nfy, relatedid)
        return idx

    def items(self):
        return self.logs.items()

    def keys(self):
        return self.logs.keys()

    def values(self):
        return self.logs.values()

    def __getitem__(self, idx) -> Notification:
        return self.logs[idx][0]

    def get_related(self, idx) -> int:
        return self.logs[idx][1]

    def get_content(self) -> str:
        ls = []
        for v in self.logs.values():
            ls.append(v[0].get_content())
        txt = ('=' * 79) + '\n'
        txt += ('\n' + ('-' * 79) + '\n').join(ls)
        txt += '\n' + ('-' * 79)
        return txt

    def get_infos(self) -> {Severity, int}:
        infos = dict()
        for s in Severity.map.values():
            infos[s] = 0
        for v in self.logs.values():
            s = v[0].severity
            infos[s] += 1
        return infos

    def have_errors(self) -> bool:
        inf = self.get_infos()
        return inf[Severity.ERROR] > 0


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
