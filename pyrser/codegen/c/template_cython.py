# Use classical C template
from pyrser.codegen.c.template_c import *

# Python Source
c_python = """
from pyrser import grammar
from pyrser.parsing.base import MetaBasicParser
from ${ctn}_generated import ${ctn} as BaseCython

class BasePython(BaseCython, metaclass=MetaBasicParser):
    _rules = {
        ${rules_attr}
    }
    def __init__(self, content: str='', stream_name: str=''):
        # the __cinit__ of BaseCython is *implicitly* called!
        # this is hard to find and is not a bug... it's feature
        pass

class ${ctn}(BasePython, grammar.Grammar):
    def __init__(self, content: str='', stream_name: str=None):
        BasePython.__init__(self, content, stream_name)
"""

# Python Attr
c_python_attr = """
        '${rule}': BaseCython.${rule},
"""

# SETUP HEADER
c_setup = """
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

${ctn}_generated = Extension("${ctn}_generated", ["${ctn}_internal.c", "${ctn}.pyx"])

setup(
    cmdclass = {'build_ext': build_ext},
    ext_modules = [${ctn}_generated]
)
"""

# PYX HEADER
c_pyx = """
cimport ${ctn}_internal

cdef class ${ctn}:
    # wrap it for python
    cdef ${ctn}_internal.${ctn}     *_inst
    cdef bytes                      _content
    cdef bytes                      _stream_name
    def __cinit__(self, content='', stream_name=''):
        # encode in utf-8 for easiest parsing
        self._stream_name = stream_name.encode('UTF-8')
        self._content = content.encode('UTF-8')
        # instanciate internal
        self._inst = ${ctn}_internal.${ctn}_new(self._content)
        if self._inst is NULL:
            raise MemoryError()

    def __dealloc(self):
        print("DEALLOC")
        if self._inst is not NULL:
            ${ctn}_internal.${ctn}_clean(self._inst)
${rfunctions_proto}
"""

# PYX RULES
c_pyx_rules = """
    def ${rule}(self):
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

# Base template for a Rule proto as a Python Function
c_pproto = """
    bint    read_${rule}(${ctn} *_self)
"""
