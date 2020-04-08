from contextlib import contextmanager
import socket
import pathlib
import io

BUFLEN = 2 ** 20 # all file/string > to 1Mo or network is buffered

class Grammar:
    def __init__(self, ffi):
        self.ffi = ffi

    def create_parser(self):
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
        self._parser.eof = 0
        self._parser.full = 0

    @contextmanager
    def from_file(self, path):
        if not isinstance(path, pathlib.Path):
            raise RuntimeError(f"'path' parameter must be a kind of pathlib.Path, recv type: {type(path)}")
        if not path.exists():
            raise RuntimeError(f"'file {path}' must exists")
        self._path = path
        self._io = open(path, 'r')
        self.create_parser()
        yield self._parser
        self._io.close()

    @contextmanager
    def from_string(self, txt):
        if not isinstance(txt, str):
            raise RuntimeError(f"'txt' parameter must be a kind str, recv type: {type(txt)}, with no relation to 'str'")
        self._txt = txt
        self._io = io.StringIO(txt)
        self.create_parser()
        yield self._parser
        self._io.close()

    @contextmanager
    def from_socket(self, sock):
        if not isinstance(sock, socket.socket):
            raise RuntimeError(f"'sock' parameter must be a kind of socket, recv type: {type(sock)}, with no relation to 'socket'")
        self._sock = sock
        self._io = sock.makefile('r')
        self.create_parser()
        yield self._parser
        self._io.close()
