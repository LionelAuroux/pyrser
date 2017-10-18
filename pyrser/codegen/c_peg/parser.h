#ifndef _PARSER_H_
#define _PARSER_H_

typedef int bool;
#define true 1
#define false 0

typedef struct position_e position_t;

struct position_e
{
    unsigned long   cur_buf;
    unsigned long   idx;
    bool            eof_reached;
};

// I/O
typedef struct iterable_stream_e its_t;

its_t   *its_from_file(const char *, position_t *);
its_t   *its_from_string(const char *, position_t *);
void    its_clean(its_t *);

bool             its_has_next(its_t *, position_t *);
const char      *its_next(its_t *, position_t *);

// PEG
typedef struct parser_e parser_t;


static inline
void    position_copy(position_t *dst, position_t *src)
{
    dst->cur_buf = src->cur_buf;
    dst->idx = src->idx;
}

struct parser_e
{
    its_t           *content;
    position_t      pos;
    const char      *current;
};

parser_t    *parser_new_from_file(const char *);
parser_t    *parser_new_from_string(const char *);
void        parser_clean(parser_t *);

static inline
char        parser_getchar(parser_t *p)
{
    // not init, or at the end of current buff and not EOF, ask a new buf
    if (!p->pos.eof_reached)
        p->pos.eof_reached = !its_has_next(p->content, &p->pos);
    if ((!p->current || !p->current[p->idx]) && !p->eof_reached)
        p->current = its_next(p->content, &p->pos);
    if (!p->current)
    {
        p->pos.eof_reached = true;
        return 0;
    }
    return p->current[p->pos.idx];
}

static inline
bool        parser_eof(parser_t *p)
{
    return p->pos.eof_reached;
}

static inline
bool         parser_peekchar(parser_t *p, char c)
{
    return parser_getchar(p) == c;
}

static inline
bool         parser_readchar(parser_t *p, char c)
{
    if (parser_peekchar(p, c))
    {
        p->idx += 1;
        return true;
    }
    return false;
}

static inline
bool         parser_readrange(parser_t *p, char a, char b)
{
    char c = parser_getchar(p);
    if (c >= a && c <= b)
    {
        p->idx += 1;
        return true;
    }
    return false;
}

static inline
bool         parser_readtext(parser_t *p, const char *txt)
{
    unsigned long i = 0;
    position_t tmp;
    
    position_copy(&tmp, &p->pos);
    while (!p->pos.eof_reached && parser_readchar(p, txt[i]))
        i += 1;
    if (!txt[i])
        return true;
    position_copy(&p->pos, &tmp);
    return false;
}

#endif
