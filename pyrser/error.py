# error handling
import os
import tempfile
import inspect
import re
import weakref
from collections import *
from pyrser import meta


Severity = meta.enum('INFO', 'WARNING', 'ERROR')


class LocationInfo:
    #__slots__ = ['filepath', 'line', 'col', 'size']

    def __init__(self, filepath: str, line: int, col: int, size: int=1):
        self.filepath = filepath
        self.line = line
        self.col = col
        self.size = size

    @staticmethod
    def from_stream(stream: 'Stream', is_error=False) -> 'LocationInfo':
        if stream._name is None and is_error is True:
            (fh, stream._name) = tempfile.mkstemp()
            tmpf = os.fdopen(fh, 'w')
            tmpf.write(stream._content)
            tmpf.close()
        return LocationInfo(
            stream._name,
            stream._cursor.lineno,
            stream._cursor.col_offset
        )

    @staticmethod
    def from_maxstream(stream: 'Stream') -> 'LocationInfo':
        if stream._name is None:
            (fh, stream._name) = tempfile.mkstemp()
            tmpf = os.fdopen(fh, 'w')
            tmpf.write(stream._content)
            tmpf.close()
        return LocationInfo(
            stream._name,
            stream._cursor._maxline,
            stream._cursor._maxcol
        )

    @staticmethod
    def from_here(pos=1):
        f = inspect.currentframe()
        fcaller = inspect.getouterframes(f)[pos]
        rstr = r'(\s+).'
        cl = re.compile(rstr)
        call = fcaller[4][0]
        m = cl.match(call)
        current_file = os.path.abspath(fcaller[1])
        li = LocationInfo(current_file, fcaller[2], len(m.group(1)) + 1)
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


class Diagnostic(Exception):
    """
    The diagnostic object is use to handle easily
    all errors/warnings/infos in a compiler that you could
    encounter. Error while parsing, Error while type checking etc...
    You could use different severity for your notification.
    """
    def __init__(self):
        self.logs = []

    def __bool__(self):
        return self.have_errors() is not True

    def notify(self, severity: Severity, msg: str,
               location: object) -> int:
        nfy = Notification(severity, msg, location)
        self.logs.append(nfy)
        return len(self.logs) - 1

    def get_content(self) -> str:
        ls = []
        for v in self.logs:
            ls.append(v.get_content())
        txt = ('=' * 79) + '\n'
        txt += ('\n' + ('-' * 79) + '\n').join(ls)
        txt += '\n' + ('-' * 79)
        return txt

    def get_infos(self) -> {Severity, int}:
        infos = dict()
        for s in Severity.map.values():
            infos[s] = 0
        for v in self.logs:
            s = v.severity
            infos[s] += 1
        return infos

    def have_errors(self) -> bool:
        inf = self.get_infos()
        return inf[Severity.ERROR] > 0
