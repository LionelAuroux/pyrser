#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include "parser_{{ parser['name'] }}.h"

{% for callback in parser['callbacks'] %}
extern int {{ callback }}_link(parser_t*);
{% endfor %}

uint32_t    peek(parser_t* s)
{
    uint32_t c = 0;
    uint8_t l = len_utf_char(s);
    printf("POS %ld %c\n", s->byte_pos, s->intern[s->byte_pos]);
    printf("intern %s\n", s->intern);
    printf("PEEK %d\n", l);
    if (s->byte_pos + l > s->intern_len)
        flush_parser_link(s);
    for (uint64_t i = s->byte_pos; i < (s->byte_pos + l); ++i)
    {
        printf("in intern %s %ld\n", s->intern, s->byte_pos);
        printf("BEFORE %d - %ld : %d\n", c, i, s->intern[i]);
        uint8_t nc = s->intern[i];
        uint8_t nsh = 0;
        if ((i - s->byte_pos) == 0)
        {
            switch (l)
            {
                case 1: // first byte of 1 byte
                    nc = nc & 127;
                    nsh = 7;
                    break;
                case 2: // first byte of 2 bytes
                    nc = nc & 31;
                    nsh = 5;
                    break;
                case 3: // first byte of 3 bytes
                    nc = nc & 15;
                    nsh = 4;
                    break;
                case 4: // first byte of 4 bytes
                    nc = nc & 7;
                    nsh = 3;
            }
        }
        else
        {
            nc = nc & 63; // continuation byte
            nsh = 6;
        }
        printf("NC %d : %d\n", nc, nsh);
        c = (c << nsh) + nc;
        printf("NEXT %d\n", c);
    }
    return c;
}

void    next_char(parser_t* s)
{//TODO: next byte_pos
    uint8_t  l = len_utf_char(s);
    if (s->byte_pos + l > s->intern_len)
        flush_parser_link(s);
    s->char_pos += 1;
    s->byte_pos += l;
}

uint64_t     get_pos(parser_t* s)
{
    return s->byte_pos;
}

void    set_pos(parser_t* s, uint64_t p)
{
    s->byte_pos = p;
}
