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

# TODO: need _link bindings
parser_c_callbacks = ["flush_parser", "info_parser"]

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
            'name': 'Base',
            'decls': parser_c_decls + parser_intern_funcs,
            'callbacks': parser_c_callbacks,
        }
    # TODO: generate header
    templ = env.get_template('parser.tmpl.h')
    with open(f'parser_{ctx["name"]}.h', 'w+') as f:
        f.write(templ.render(parser=ctx))

    # TODO: generate C code
    templ = env.get_template('parser.tmpl.c')
    with open(f'parser_{ctx["name"]}.c', 'w+') as f:
        f.write(templ.render(parser=ctx))

    # TODO: generate Python code
    templ = env.get_template('wrapper.tmpl.py')
    with open(f'parser_{ctx["name"]}.py', 'w+') as f:
        f.write(templ.render(parser=ctx))

    for decl in parser_c_decls:
        ffibuilder.cdef(decl)

    # FOR DEBUG
    for decl in parser_intern_funcs:
        ffibuilder.cdef(decl)

    source_txt = f"""
        #include "parser_{ctx['name']}.h"
    """

    for ext_decl in parser_c_callbacks:
        ffibuilder.cdef(f'extern "Python" int {ext_decl}(parser_t *);')
        source_txt += f'static int {ext_decl}(parser_t *);\n'
        source_txt += f"int {ext_decl}_link(parser_t *s)" + " { return " + ext_decl + "(s); }\n"
    
    # TODO: must generate it for given grammar
    ffibuilder.set_source("lib_" + ctx['name'], source_txt, sources=[f'parser_{ctx["name"]}.c'])

    # Makefile features
    print(f"{pformat(vars(ffibuilder))}")
    for it in ffibuilder._assigned_source[3]['sources']:
        print(f"SOURCE {it}")
    ffibuilder.compile(verbose=True)
