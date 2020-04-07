from contextlib import contextmanager
import io

BUFLEN = 4096

class Grammar:
    def __init__(self, ffi):
        self.ffi = ffi

    @contextmanager
    def from_file(self, fn):
        self._fn = fn
        self._io = open(fn, 'r')
        self._parser = self.ffi.new("parser_t*")
        self._parser_self = self.ffi.new_handle(self) # warning: to avoid gc
        self._parser.self = self._parser_self
        self._buf = b""
        self._buf_intern = None
        print(f"ID IO {self._parser.self}")
        self._parser.intern_len = 0
        self._parser.intern = self.ffi.new("char*", None)
        self._parser.char_pos = 0
        self._parser.byte_pos = 0
        yield self._parser
        self._io.close()

    @contextmanager
    def from_string(self, txt):
        self._txt = txt
        self._io = io.StringIO(txt)
        self._parser = self.ffi.new("parser_t*")
        self._parser_self = self.ffi.new_handle(self) # warning: to avoid gc
        self._parser.self = self._parser_self
        self._buf = b""
        self._buf_intern = None
        print(f"ID IO {self._parser.self}")
        self._parser.intern_len = 0
        self._parser.intern = self.ffi.new("char*", None)
        self._parser.char_pos = 0
        self._parser.byte_pos = 0
        yield self._parser
        self._io.close()
