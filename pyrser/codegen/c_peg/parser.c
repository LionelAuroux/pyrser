#include "parser.h"
#include "list.h"
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <string.h>
#include <unistd.h>

// I/O
struct iterable_stream_interface
{
    bool             (*has_next)(its_t *, position_t *);
    const char      *(*next)(its_t *, position_t *);
};

struct iterable_stream_e
{
    struct iterable_stream_interface    *itf;
};

struct iterable_stream_file_e
{
    struct iterable_stream_e    base;
    int                         fd;
    list_buf_t                  *lsbuf;
    bool                        eof;
};

struct iterable_stream_string_e
{
    struct iterable_stream_e    base;
    const char                  *content;
    unsigned long               len;
};

bool             file_has_next(its_t *, position_t *);
const char      *file_next(its_t *, position_t *);

static struct iterable_stream_interface file_itf = {file_has_next, file_next};

its_t   *its_from_file(const char *f, position_t *p)
{
    struct its_from_file_e *this = malloc(sizeof(struct iterable_stream_file_e));
    this->itf = &file_itf;
    this->fd = open(f, O_RDONLY);
    this->lsbuf = list_new();
    this->eof = false;
    p->cur_buf = 0;
    p->idx = 0;
    return (its_t*) itsf;
}

bool             file_has_next(its_t *its, position_t *p)
{
    struct iterable_stream_file_e *this = (struct iterable_stream_file_e *)its;

    return this->eof;
}
#define BUF_READ 4096
const char      *file_next(its_t *its, position_t *p)
{
    struct iterable_stream_file_e *this = (struct iterable_stream_file_e *)its;

    const char *buf = malloc(BUF_READ);
    ssize_t len = read(this->fd, buf, BUF_READ);
    if (!len)
    {
        free(buf);
        this->eof = true;
        return NULL;
    }
    list_append(this->lsbuf, buf);
    p->cur_buf += 1;
    p->idx = 0;
    return buf;
}

bool             string_has_next(its_t *, position_t *);
const char      *string_next(its_t *, position_t *);

static struct iterable_stream_interface string_itf = {string_has_next, 0};

its_t   *its_from_string(const char *s, position_t *p)
{
    struct its_from_string_e *itss = malloc(sizeof(struct iterable_stream_file_e));
    itss->itf = &string_itf;
    itfs->content = s;
    itfs->len = strlen(s);
    p->cur_buf = 0;
    p->idx = 0;
    return (its_t*) itss;
}

bool             string_has_next(its_t *its, position_t *p)
{
    return false;
}

void    its_clean(its_t *its)
{
    free(its);
}

bool             its_has_next(its_t *its, position_t *p)
{
    return its->itf.has_next(its, p);
}

const char      *its_next(its_t *its, position_t *p)
{
    return its->itf.next(its, p);
}

// PEG
parser_t    *parser_new_from_file(const char *f)
{}

parser_t    *parser_new_from_string(const char *s)
{}

#if DEBUG

#include <stdio.h>
// inclu ses tests unitaires

int main(int ac, char **av)
{
    printf("TU Parsing PEG\n");
}
#endif
