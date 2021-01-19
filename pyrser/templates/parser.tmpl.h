#ifndef __PARSER_{{ parser['name'] }}_H
#define __PARSER_{{ parser['name'] }}_H

#include <stdint.h>

{% for decl in parser['decls'] %}
{{ decl }}
{% endfor %}

{% for callback in parser['callbacks'] %}
extern uint8_t {{ callback }}_link(parser_t*);
{% endfor %}

// standard parsing functions
uint32_t        peek(parser_t *);
void            next_char(parser_t *);
uint8_t         get_pos(parser_t *, location_t *);
uint8_t         set_pos(parser_t *, location_t *);

// terminal rules
uint8_t             read_eof(parser_t *);
uint8_t             read_char(parser_t *, uint32_t);
uint8_t             read_text(parser_t *, uint8_t *);
uint8_t             read_range(parser_t *, uint32_t, uint32_t);


// TODO: grammar rules


///// STATIC INLINES
static inline uint8_t               read_eof_in(parser_t *);
static inline uint8_t               read_char_in(parser_t *, uint32_t);
static inline uint8_t               read_text_in(parser_t *, uint8_t *);
static inline uint8_t               read_range_in(parser_t *, uint32_t, uint32_t);

static inline uint8_t         get_pos_in(parser_t *p, location_t *l)
{
    l->source = p->loc.source;
    l->line = p->loc.line;
    l->cols = p->loc.cols;
    l->char_pos = p->loc.char_pos;
    l->byte_pos = p->loc.byte_pos;
    return 1;
}

static inline uint8_t         set_pos_in(parser_t *p, location_t *l)
{
    p->loc.source = l->source;
    p->loc.line = l->line;
    p->loc.cols = l->cols;
    p->loc.char_pos = l->char_pos;
    p->loc.byte_pos = l->byte_pos;
    return 1;
}

static inline uint8_t       len_utf_char_in(uint8_t c0)
{ // assume valid utf-8 encoding
    if (c0 <= 0x7f) // only 1 byte
        return 1;
    if (c0 >= 0xc0 && c0 <= 0xdf) // only 2 bytes
        return 2;
    if (c0 >= 0xe0 && c0 <= 0xef) // only 3 bytes
        return 3;
    if (c0 >= 0xf0 && c0 <= 0xf4) // only 4 bytes
        return 4;
    return 0;
}

static inline uint32_t      peekutf8_in(uint8_t *t, uint64_t *p)
{
    uint8_t l = len_utf_char_in(*t);
    //printf("PEEKBUF %d\n", l);
    uint32_t c = 0;
    for (uint64_t i = 0; i < l; ++i)
    {
        uint8_t nc = t[i];
        uint8_t nsh = 0;
        if (i == 0)
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
        c = (c << nsh) + nc;
    }
    //printf("PEEKCHAR %d\n", c);
    *p = l;
    return c;
}

static inline uint32_t      peek_in(parser_t *p)
{
    //printf("intern %s\n", p->intern);
    //printf("POS %ld -> %c\n", p->byte_pos, p->intern[p->byte_pos]);
    uint8_t  l = len_utf_char_in(p->intern[p->loc.byte_pos]);
    uint64_t newpos = l + p->loc.byte_pos;
    uint64_t old = p->intern_len;
    //printf("NEWPOS %ld ?? %ld\n", newpos, old);
    if (!p->full && newpos > old)
    {
        flush_parser_link(p); // TODO: rename to fetch
        //printf("FLUSH %ld -> %ld\n", old, p->intern_len);
       if (old == p->intern_len)
            p->full = 1;
    }
    uint64_t p0 = 0;
    return peekutf8_in(&p->intern[p->loc.byte_pos], &p0);
}

static inline void          next_char_in(parser_t *p)
{//TODO: line/cols
    uint8_t c = p->intern[p->loc.byte_pos];
    uint8_t l = len_utf_char_in(c);
    p->loc.char_pos += 1;
    p->loc.cols += 1;
    p->loc.byte_pos += l;
    if (c == '\n')
    {
        p->loc.line += 1;
        p->loc.cols = 1;
    }
}

//////// STATIC INLINES: terminal rules
static inline uint8_t                     read_eof_in(parser_t *p)
{
    return p->eof;
}

static inline uint8_t                     read_char_in(parser_t *p, uint32_t c)
{
    if (peek_in(p) == c)
    {
        next_char_in(p);
        return 1;
    }
    return 0;
}

static inline uint8_t                     read_text_in(parser_t *p, uint8_t *t)
{
    //printf("READTEXT\n");
    while (*t && peek_in(p) != 0)
    {
        //printf("POS %ld -> '%c' %d\n", p->byte_pos, p->intern[p->byte_pos], p->intern[p->byte_pos]);
        //printf("FULL %d EOF %d\n", p->full, p->eof);
        uint64_t p1 = 0;
        uint32_t c1 = peekutf8_in(t, &p1);

        uint32_t c2 = peek_in(p);
        
        //printf("cmp %d %d\n", c1, c2);
        if (c1 != c2)
            return 0;

        t += p1;
        //printf("next pos +%ld\n", p1);
        next_char_in(p);
    }
    if (*t) // if not at the end
        return 0;
    return 1;
}

static inline uint8_t                     read_range_in(parser_t *p, uint32_t b, uint32_t e)
{
    uint32_t c = peek_in(p);
    if (c >= b && c <= e)
    {
        next_char_in(p);
        return 1;
    }
    return 0;
}
#endif
