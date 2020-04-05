from cffi import FFI
from jinja2 import Environment, PackageLoader
from pprint import pformat

parser_c_decls = [
    """
    typedef struct parser_s
    {
        void        *self;
        uint8_t     *intern;
        uint64_t    intern_len;
        uint64_t    char_pos;
        uint64_t    byte_pos;
    }
    parser_t;
    """,
]

parser_c_callbacks = [
    """
    void flush_parser(parser_t*)
    """,
    """
    void info_parser(parser_t*)
    """,
]

## FOR DEBUG
parser_intern_funcs = [
    "uint32_t       peek(parser_t*);",
    "void           next_char(parser_t*);",
    "uint64_t       get_pos(parser_t*);",
    "void           set_pos(parser_t*, uint64_t);",
]

def compile():
    ffibuilder = FFI()
    env = Environment(
            loader=PackageLoader('pyrser', 'templates'),
            autoescape=False
        )
    ctx = {
            'decls': parser_c_decls + parser_intern_funcs,
            'callbacks': parser_c_callbacks,
        }
    # TODO: generate header
    templ = env.get_template('parser.tmpl.h')
    with open('parser.h', 'w+') as f:
        f.write(templ.render(parser=ctx))

    # TODO: generate C code
    templ = env.get_template('parser.tmpl.c')
    with open('parser.c', 'w+') as f:
        f.write(templ.render(parser=ctx))

    # TODO: generate Python code
    templ = env.get_template('wrapper.tmpl.py')
    with open('wrapper_parser.py', 'w+') as f:
        f.write(templ.render(parser=ctx))

    for decl in parser_c_decls:
        ffibuilder.cdef(decl)

    # FOR DEBUG
    for decl in parser_intern_funcs:
        ffibuilder.cdef(decl)

    source_txt = """
        #include "parser.h"
    """

    for ext_decl in parser_c_callbacks:
        ffibuilder.cdef(f'extern "Python" {ext_decl};')
        source_txt += f'static {ext_decl};\n'

    source_txt += """

    void flush_parser_link(parser_t *s) { flush_parser(s);}
    """
    
    # TODO: must generate it for given grammar
    ffibuilder.set_source("lib_parser", source_txt, sources=['parser.c'])

    # Makefile features
    print(f"{pformat(vars(ffibuilder))}")
    for it in ffibuilder._assigned_source[3]['sources']:
        print(f"SOURCE {it}")
    ffibuilder.compile(verbose=True)
