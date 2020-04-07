#ifndef __PARSER_{{ parser['name'] }}_H
#define __PARSER_{{ parser['name'] }}_H

#include <stdint.h>

{% for decl in parser['decls'] %}
{{ decl }}
{% endfor %}

uint32_t        peek(parser_t*);
void            next_char(parser_t*);
uint64_t        get_pos(parser_t*);
void            set_pos(parser_t*, uint64_t);

static inline uint8_t len_utf_char(parser_t *s)
{ // assume valid utf-8 encoding
    uint8_t c0 = s->intern[s->byte_pos];
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

static inline uint8_t intern_utf_char(parser_t *s)
{ // assume valid utf-8 encoding
    uint8_t c0 = s->intern[s->byte_pos];
    if (c0 >= 0x80 && c0 <= 0xbf) // intermediate bytes
        return 1;
    return 0;
}

#endif
