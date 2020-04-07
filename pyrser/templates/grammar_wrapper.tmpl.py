from pyrser.parser.grammar import Grammar
from .lib_{{ parser['name'] }} import ffi, lib
import io
from contextlib import contextmanager

BUFLEN = 4096

class {{ parser['name'] }}(Grammar):
    def __init__(self):
        Grammar.__init__(self, ffi)

@ffi.def_extern()
def flush_parser(p: 'parser_t') -> int:
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
    return 1
    

@ffi.def_extern()
def info_parser(p: 'parser_t') -> int:
    print(f"INFO FROM PYTHON: LEN {p.intern_len}")
    print(f"INFO FROM PYTHON: SELF {p.self}")
    print(f"INFO FROM PYTHON: INTERN {p.intern}")
    print(f"INFO FROM PYTHON: CP {p.char_pos}")
    print(f"INFO FROM PYTHON: BP {p.byte_pos}")
    return 1
