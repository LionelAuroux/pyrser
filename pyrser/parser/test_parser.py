import pyrser.parser.Base as pb
import sys
import logging
import pathlib as pl

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s', handlers=[logging.StreamHandler(sys.stdout)])
here = pl.Path(__file__).resolve().parent

def test_parser_00():
    from pyrser.parser import builder
    here = pl.Path(__file__).resolve().parent
    builder.compile(here / 'Base')

def test_parser_01():
    logging.debug("COOL")
    g = pb.Base()
    pb.BUFLEN = 4
    # file and basic peek/next
    with g.from_file(here / 'Base' / "parser_Base.h") as p:
        assert p is not None, "Init"
        pb.info_parser(p)
        pb.flush_parser(p)
        assert pb.lib.peek(p) == ord('#'), 'failed to peek'
        assert pb.lib.get_pos(p) == 0, 'failed to get'
        pb.lib.next_char(p)
        assert pb.lib.get_pos(p) == 1, 'failed to get'
        assert pb.lib.peek(p) == ord('i'), 'failed to peek'

    # string and unicode peek/next
    print("*" * 20)
    pb.BUFLEN = 4
    #with g.from_string("t\N{white chess king}") as p:
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
