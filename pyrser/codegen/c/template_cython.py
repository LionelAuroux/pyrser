
# SETUP HEADER
c_setup = """
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

${ctn} = Extension("${ctn}", ["${ctn}_internal.c", "${ctn}.pyx"])

setup(
    cmdclass = {'build_ext': build_ext},
    ext_modules = [${ctn}]
)
"""

# PYX HEADER
c_pyx = """
cimport ${ctn}_internal

cdef class ${ctn}:
    # wrap it for python
    cdef ${ctn}_internal.${ctn}     *_inst
    cdef bytes                      _content
    def __cinit__(self, content):
        # encode in utf-8 for easiest parsing
        _content = content.encode('UTF-8')
        self._inst = ${ctn}_internal.${ctn}_new(_content)
        if self._inst is NULL:
            raise MemoryError()

    def __dealloc(self):
        if self._inst is not NULL:
            ${ctn}_internal.${ctn}_clean(self._inst)
${rfunctions_proto}
"""

# PYX RULES
c_pyx_rules = """
    def read_${rule}(self):
        return ${ctn}_internal.read_${rule}(self._inst)
"""

# PXD HEADER
c_pxd = """
cdef extern from "${ctn}_internal.h":
    ctypedef struct ${ctn}:
        pass
    ${ctn}      *${ctn}_new(char *)
    void        ${ctn}_clean(${ctn} *)
    # convert int to boolean use bint
    ${pfunctions_proto}
"""

# Header STUB
c_header = """
typedef struct
{
    char *_stream;
} ${ctn};

${ctn}  *${ctn}_new(char *content);
void    ${ctn}_clean(${ctn} *);
${cfunctions_proto}
"""

# Base template for a Rule proto as a Python Function
c_pproto = """
    bint    read_${rule}(${ctn} *_self)
"""

# Base template for a Rule proto as a C Function
c_cproto = """
int    read_${rule}(${ctn} *_self);
"""

# Source code STUB
c_file = """
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
c_function = """
int     read_${rule}(${ctn} *_self)
{
    int _res = FALSE;
    char *_tmp${altid} = _self->_stream;
    ${code}
    next_${nextid}:
        __attribute__ ((__unused__))
    end_${altid}:
        __attribute__ ((__unused__))
    if (_res)
    {   _self->_stream = _tmp${altid};}
    return _res;
}
"""

# Base template for read a Char
c_char = """
    if (*_tmp${altid} == '${char}')
    {
        _tmp${altid} += 1;
        _res = TRUE;
    }
    else
    {   goto next_${nextid};}
"""

# header for Alternatives
c_althead = """
    {
        char *_tmp${altid} = _tmp${outid};
"""

# Code for each Alternative
c_alt = """
        ${code}
        _tmp${outid} = _tmp${altid};
        _res = TRUE;
        goto end_${altid};
    next_${nextid}:
        __attribute__ ((__unused__))
"""

# footer for Alternatives
c_altfoot = """
    _res = FALSE;
    goto next_${nextid};
    end_${altid}:
        __attribute__ ((__unused__))
    _tmp${outid} = _tmp${altid};
    }
"""

