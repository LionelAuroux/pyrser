#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include "parser_{{ parser['name'] }}.h"

uint32_t            peek(parser_t *p)
{
    return peek_in(p);
}

void                next_char(parser_t *p)
{
    next_char_in(p);
}

uint8_t             get_pos(parser_t *p, location_t *l)
{
    return get_pos_in(p, l);
}

uint8_t             set_pos(parser_t *p, location_t *l)
{
    return set_pos_in(p, l);
}

// terminal rules
uint8_t             read_eof(parser_t *p)
{
    return read_eof_in(p);
}

uint8_t             read_char(parser_t *p, uint32_t c)
{
    return read_char_in(p, c);
}

uint8_t             read_text(parser_t *p, uint8_t *t)
{
    return read_text_in(p, t);
}

uint8_t             read_range(parser_t *p, uint32_t b, uint32_t e)
{
    return read_range_in(p, b, e);
}
