# error handling
import os
import atexit
import tempfile
import inspect
import re
import weakref
from collections import *
from pyrser import meta


Severity = meta.enum('INFO', 'WARNING', 'ERROR')


class LocationInfo:
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
            atexit.register(os.remove, stream._name)
        loc = LocationInfo(
            stream._name,
            stream._cursor.lineno,
            stream._cursor.col_offset
        )
        return loc

    @staticmethod
    def from_maxstream(stream: 'Stream', is_error=False) -> 'LocationInfo':
        if stream._name is None:
            (fh, stream._name) = tempfile.mkstemp()
            tmpf = os.fdopen(fh, 'w')
            tmpf.write(stream._content)
            tmpf.close()
            atexit.register(os.remove, stream._name)
        loc = LocationInfo(
            stream._name,
            stream._cursor._maxline,
            stream._cursor._maxcol
        )
        return loc

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
        # by default the idiom list(f) don't count the last line if the last line is empty (nothing between last \n and EOF)
        if self.line > 1:
            lastindex = self.line - 1
        else:
            lastindex = 0
            self.line = 1
        if lastindex >= len(lines):
            lastindex = len(lines) - 1
            self.line = lastindex + 1
            self.col = len(lines[lastindex])
        txtline = lines[lastindex]
        if txtline[-1] != '\n':
            txtline += '\n'
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
                 location: LocationInfo=None, details: str=None):
        self.severity = severity
        self.location = location
        self.msg = msg
        self.details = details

    def get_content(self, with_locinfos=False, with_details=False) -> str:
        sevtxt = ""
        txt = "{s} : {msg}\n".format(
            s=Severity.rmap[self.severity].lower(),
            msg=self.msg
        )
        if with_locinfos and self.location is not None:
            txt += self.location.get_content()
        if with_details and self.details is not None:
            txt += self.details
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
        return self.have_errors

    def __str__(self) -> str:
        return self.get_content(with_details=True)

    def notify(self, severity: Severity, msg: str,
               location: LocationInfo=None, details: str=None) -> int:
        nfy = Notification(severity, msg, location, details)
        self.logs.append(nfy)
        return len(self.logs) - 1

    def add(self, n: Notification) -> int:
        if not isinstance(n, Notification):
            raise TypeError("Must be a notification")
        self.logs.append(n)
        return len(self.logs) - 1

    def get_content(self, with_locinfos=True, with_details=False) -> str:
        # TODO: First an update Error Infos and then get_content only retrieve calculate data
        ls = []
        for v in self.logs:
            ls.append(v.get_content(with_locinfos, with_details))
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

    @property
    def have_errors(self) -> bool:
        for v in self.logs:
            if v.severity == Severity.ERROR:
                return True
