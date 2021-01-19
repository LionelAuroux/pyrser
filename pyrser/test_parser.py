import sys
import logging
import pathlib as pl

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s', handlers=[logging.StreamHandler(sys.stdout)])
here = pl.Path(__file__).resolve().parent

def test_parser_00():
    from pyrser import builder
    here = pl.Path(__file__).resolve().parent
    base_path = here / 'Base'
    if base_path.exists():
        import shutil
        shutil.rmtree(base_path, ignore_errors=True)
    builder.compile(base_path)
    assert base_path.exists(), "failed to make ouput dir during compile"
    assert (base_path / '__init__.py').exists(), "failed to process __init__.py during compile"
    assert (base_path / 'grammar_Base.py').exists(), "failed to process grammar_Base.py during compile"
    lib_path = list(base_path.glob("lib_Base.*.so"))
    assert len(lib_path) == 1, "failed to comile the .so dynlib"
    assert lib_path[0].exists(), "failed to compile"
    

def test_parser_01():
    from . import Base as pb
    logging.debug("COOL")
    g = pb.Base()
    pb.BUFLEN = 4
    # file and basic peek/next
    newpos = pb.ffi.new("location_t*")
    with g.from_file(here / 'Base' / "parser_Base.h") as p:
        assert p is not None, "Init"
        pb.info_parser(p)
        pb.flush_parser(p)
        assert pb.lib.peek(p) == ord('#'), 'failed to peek'
        pb.lib.get_pos(p, newpos)
        assert newpos.byte_pos == 0, 'failed to get'
        pb.lib.next_char(p)
        pb.lib.get_pos(p, newpos)
        assert newpos.byte_pos == 1, 'failed to get'
        assert pb.lib.peek(p) == ord('i'), 'failed to peek'

    # string and unicode peek/next
    print("*" * 20)
    with g.from_string("toto cool") as p:
        assert pb.lib.peek(p) == ord('t'), 'failed to peek'
        pb.lib.next_char(p)
        assert pb.lib.peek(p) == ord('o'), 'failed to peek'
        pb.lib.next_char(p)
        assert pb.lib.read_char(p, ord('t')), "failed to read"
        assert pb.lib.read_text(p, b'o cool'), "failed to read"
    
    # unicode
    with g.from_string("t\N{white chess king}") as p:
        assert pb.lib.peek(p) == ord('t'), 'failed to peek'
        pb.lib.next_char(p)
        assert pb.lib.peek(p) == ord('\N{white chess king}'), 'failed to peek'

    # socket
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("www.python.org", 80))
    with g.from_socket(s) as p:
        s.sendall(b"GET / HTTP/1.1\r\nHost: www.python.org\r\nConnection: close\r\n\r\n")
        assert pb.lib.read_text(p, b"HTTP/1.1"), "failed to read"
        assert pb.lib.read_text(p, b" 301"), "failed to read"
        assert pb.lib.read_text(p, b" Moved Permanently\n"), "failed to read"
        assert pb.lib.read_text(p, b"Server: Varnish\n"), "failed to read"

