from pyrser.parser.lib_parser import ffi
import io
from contextlib import contextmanager

BUFLEN = 4096

class Grammar:
    def __init__(self):
        pass

    @contextmanager
    def from_file(self, fn):
        self._fn = fn
        self._io = open(fn, 'r')
        self._parser = ffi.new("parser_t*")
        self._parser_self = ffi.new_handle(self) # warning: to avoid gc
        self._parser.self = self._parser_self
        self._buf = b""
        self._buf_intern = None
        print(f"ID IO {self._parser.self}")
        self._parser.intern_len = 0
        self._parser.intern = ffi.new("char*", None)
        self._parser.char_pos = 0
        self._parser.byte_pos = 0
        yield self._parser
        self._io.close()

    @contextmanager
    def from_string(self, txt):
        self._txt = txt
        self._io = io.StringIO(txt)
        self._parser = ffi.new("parser_t*")
        self._parser_self = ffi.new_handle(self) # warning: to avoid gc
        self._parser.self = self._parser_self
        self._buf = b""
        self._buf_intern = None
        print(f"ID IO {self._parser.self}")
        self._parser.intern_len = 0
        self._parser.intern = ffi.new("char*", None)
        self._parser.char_pos = 0
        self._parser.byte_pos = 0
        yield self._parser
        self._io.close()

@ffi.def_extern()
def flush_parser(p: 'parser_t'):
    global BUFLEN
    print(f"FLUSH IO {p}")
    if p.byte_pos == p.intern_len:
        print(f"IO: {p.self}")
        self = ffi.from_handle(p.self) # get self object
        io = self._io # get IO object
        self._buf = self._buf + bytes(io.read(BUFLEN), 'utf-8') #######
        print(f"IO: {self._buf}")
        p.intern_len = len(self._buf)
        self._buf_intern = ffi.new("char[]", self._buf) # warning: to avoid gc
        p.intern = self._buf_intern
        p.byte_pos = 0
    

@ffi.def_extern()
def info_parser(p: 'parser_t'):
    print(f"INFO FROM PYTHON: LEN {p.intern_len}")
    print(f"INFO FROM PYTHON: SELF {p.self}")
    print(f"INFO FROM PYTHON: INTERN {p.intern}")
    print(f"INFO FROM PYTHON: CP {p.char_pos}")
    print(f"INFO FROM PYTHON: BP {p.byte_pos}")
