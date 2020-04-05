import pyrser.parser.wrapper_parser as wp
import sys
import logging
from lib_parser.lib import peek, next_char, set_pos, get_pos

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s', handlers=[logging.StreamHandler(sys.stdout)])


def test_parser_01():
    logging.debug("COOL")
    g = wp.Grammar()
    wp.BUFLEN = 4
    # file and basic peek/next
    with g.from_file("parser.h") as p:
        assert p is not None, "Init"
        wp.info_parser(p)
        wp.flush_parser(p)
        assert peek(p) == ord('#'), 'failed to peek'
        assert get_pos(p) == 0, 'failed to get'
        next_char(p)
        assert get_pos(p) == 1, 'failed to get'
        assert peek(p) == ord('i'), 'failed to peek'

    # string and unicode peek/next
    print("*" * 20)
    #with g.from_string("t\N{white chess king}") as p:
    with g.from_string("totot") as p:
        assert peek(p) == ord('t'), 'failed to peek'
        next_char(p)
        assert peek(p) == ord('o'), 'failed to peek'
        
    with g.from_string("t\N{white chess king}") as p:
        assert peek(p) == ord('t'), 'failed to peek'
        next_char(p)
        assert peek(p) == ord('\N{white chess king}'), 'failed to peek'
