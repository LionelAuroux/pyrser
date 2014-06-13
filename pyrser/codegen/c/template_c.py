# Raw C Templates
# Note:
# To avoid the handling of an internal state for the status of the last evaluation
# we just follow positionnal convention inside C templates
# after a ${code} or at the end of a primitive template your last evaluation IS TRUE
# FALSE on last evaluation lands into the nearest error_${errid} label

# Header
c_header = """// This FILE is Generated DO NOT EDIT
typedef struct
{
    char *_stream;
} ${ctn};

${ctn}  *${ctn}_new(char *content);
void    ${ctn}_clean(${ctn} *);
${cfunctions_proto}
"""

# Base template for a Rule proto as a C Function
c_cproto = """\
int    read_${rule}(${ctn} *_self);
"""

# Source code STUB
c_file = """// This FILE is Generated DO NOT EDIT
#include <stdlib.h>
#include <stdio.h>
#include "${ctn}_internal.h"

#define TRUE    1
#define FALSE   0

${ctn}     *${ctn}_new(char *content)
{
    ${ctn} *self = calloc(1, sizeof(${ctn}));
    self->_stream = content;
    return self;
}

void            ${ctn}_clean(${ctn} *_self)
{
    free(_self);
}
"""

# Base template for a Rule as a C Function
c_function = """\
int     read_${rule}(${ctn} *_self)
{
    char *_tmp${lvlid} = _self->_stream;
    ${code}
    _self->_stream = _tmp${lvlid};
    return TRUE;
    error_${errid}:
        __attribute__ ((__unused__))
        return FALSE;
}
"""

# === SEQ ===
# header for Sequences
c_seqhead = """\
    {
        char *_tmp${lvlid} = _tmp${outid};
"""

# code for each sequence
c_seq = """\
        ${code}
"""

# footer for Sequences
c_seqfoot = """\
    //seqfoot
        goto end_${errid};
        error_${errid}: __attribute__ ((__unused__))
            goto error_${outerrid};
        end_${errid}: __attribute__ ((__unused__))
            _tmp${outid} = _tmp${lvlid};
    }\
"""

# ===

# === ALT ===
# header for Alternatives
c_althead = """\
    {
        char *_tmp${lvlid} = _tmp${outid};
"""

# Code for each Alternative
c_alt = """\
    //alt
        ${code}
        // ALT
        goto end_${outerrid};
        error_${errid}: __attribute__ ((__unused__))
        _tmp${lvlid} = _tmp${outid};
"""

# footer for Alternatives
c_altfoot = """\
    //altfoot
        // for the last alternative reach end_... as else of if statement
        if (_tmp${lvlid} == _tmp${outid})
        {   goto error_${outerrid};}
        end_${errid}: __attribute__ ((__unused__))
            _tmp${outid} = _tmp${lvlid};
    }\
"""
# ===

# === REPEATERS ===
# rep0n
c_rep0n = """\
    {
        char *_tmp${lvlid} = _tmp${outid};
        char *__tmp = _tmp${lvlid};
        while (TRUE)
        {
            ${code}
            // REP0N
            _tmp${outid} = _tmp${lvlid};
            continue;
            error_${errid}: __attribute__ ((__unused__))
                break;
        }
        // error if not consume
        if (_tmp${lvlid} == __tmp)
        {   goto error_${outerrid};}
    }\
"""

# rep1n
c_rep1n = """\
    {
        char *_tmp${lvlid} = _tmp${outid};
        int _cpt = 0;
        while (TRUE)
        {
            ${code}
            _tmp${outid} = _tmp${lvlid};
            _cpt += 1;
            continue;
            error_${errid}: __attribute__ ((__unused__))
                break;
        }
        // error if not one match
        if (_cpt == 0)
        {   goto error_${outerrid};}
    }\
"""

# repopt
c_repopt = """\
    {
        char *_tmp${lvlid} = _tmp${outid};
        ${code}
        _tmp${outid} = _tmp${lvlid};
        error_${errid}: __attribute__ ((__unused__))
        //semicolon to avoid "error: label at end of compound statement"
        ;
    }\
"""
# ===

# === !,~,!!,-> ===
c_neg = """\
    {
        char *_tmp${lvlid} = _tmp${outid};
        ${code}
        goto error_${outerrid};
        error_${errid}: __attribute__ ((__unused__))
        // semicolon to avoid "error: label at end of compound statement"
        ;
    }\
"""

c_complement = """\
    {
        // complement
        char *_tmp${lvlid} = _tmp${outid};
        ${code}
        goto error_${outerrid};
        error_${errid}: __attribute__ ((__unused__))
            if (*_tmp${outid} != 0)
            {   _tmp${outid} += 1;}
            else
            {   goto error_${outerrid};}
    }\
"""

c_lookahead = """
    {
        char *_tmp${lvlid} = _tmp${outid};
        ${code}
        goto nothing_${errid};
        error_${errid}: __attribute__ ((__unused__))
            goto error_${outerrid};
        nothing_${errid}: __attribute__ ((__unused__))
        // semicolon to avoid "error: label at end of compound statement"
        ;
    }\
"""

c_until = """
    {
        char *_tmp${lvlid};
        char *__tmpreset = _tmp${outid};
        while (TRUE)
        {
            _tmp${lvlid} = _tmp${outid};
            ${code}
            break;
            error_${errid}: __attribute__ ((__unused__))
                if (*_tmp${lvlid} == 0)
                {
                    _tmp${outid} = __tmpreset;
                    goto error_${outerrid};
                }
                _tmp${outid} += 1;
        }
    }
"""

# ===

# === BASE PRIMITIVE ===
# Base template for read a Char
c_char = """\
    if (*_tmp${lvlid} != '${char}')
    {   goto error_${errid};}
    _tmp${lvlid} += 1;\
"""

# Base template for read a Range
c_range = """\
    if (*_tmp${lvlid} < '${char_begin}' || *_tmp${lvlid} > '${char_end}')
    {   goto error_${errid};}
    _tmp${lvlid} += 1;\
"""

# Base template for read a Text
c_text = """\
    {
        char *_text = "${text}";
        char *__tmp = _tmp${lvlid};
        while (*_text != 0)
        {
            if (*__tmp != *_text)
            {   goto error_${errid};}
            __tmp += 1;
            _text += 1;
        }
        _tmp${lvlid} = __tmp;
    }\
"""
