import pyrser.parser.parser_Base as pb
import sys
import logging
import pathlib as pl

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s', handlers=[logging.StreamHandler(sys.stdout)])
here = pl.Path(__file__).resolve().parent


def test_parser_01():
    logging.debug("COOL")
    g = pb.Base()
    pb.BUFLEN = 4
    # file and basic peek/next
    with g.from_file(here / "parser_Base.h") as p:
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
    #with g.from_string("t\N{white chess king}") as p:
    with g.from_string("totot") as p:
        assert pb.lib.peek(p) == ord('t'), 'failed to peek'
        pb.lib.next_char(p)
        assert pb.lib.peek(p) == ord('o'), 'failed to peek'
        
    with g.from_string("t\N{white chess king}") as p:
        assert pb.lib.peek(p) == ord('t'), 'failed to peek'
        pb.lib.next_char(p)
        assert pb.lib.peek(p) == ord('\N{white chess king}'), 'failed to peek'
