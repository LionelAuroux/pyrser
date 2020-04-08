from cffi import FFI
from jinja2 import Environment, PackageLoader
from pprint import pformat
import pathlib as pl

parser_c_decls = [
    """
    typedef struct location_s
    {
        uint8_t     *source;
        uint64_t    line;
        uint64_t    cols;
        uint64_t    char_pos;
        uint64_t    byte_pos;
    }
    location_t;
    """,
    """
    typedef struct parser_s
    {
        void        *self;
        uint8_t     *intern;
        uint64_t    intern_len;
        uint64_t    char_pos;
        uint64_t    byte_pos;
        uint8_t     eof;   // TODO: flags for many states
        uint8_t     full;   // TODO: flags for many states
    }
    parser_t;
    """,
]

# TODO: need _link bindings
parser_c_callbacks = ["flush_parser", "info_parser"]

## FOR DEBUG
parser_intern_funcs = [
    # intern
    "uint32_t               peek(parser_t*);",
    "void                   next_char(parser_t*);",
    "uint64_t               get_pos(parser_t*);",
    "void                   set_pos(parser_t*, uint64_t);",
    # terminal rules
    "uint8_t                read_eof(parser_t *);",
    "uint8_t                read_char(parser_t *, uint32_t);",
    "uint8_t                read_text(parser_t *, uint8_t *);",
    "uint8_t                read_range(parser_t *, uint32_t, uint32_t);",
]

def compile(pkg_path: pl.Path):
    if not pkg_path.exists():
        pkg_path.mkdir()
    if not pkg_path.is_dir():
        raise RuntimeError(f"{pkg_path} already exists and is not a directory")

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
    # generate __init__.py
    templ = env.get_template('__init__.tmpl.py')
    with open(pkg_path / "__init__.py", 'w+') as f:
        f.write(templ.render(parser=ctx))

    # generate header
    templ = env.get_template('parser.tmpl.h')
    with open(pkg_path / f'parser_{ctx["name"]}.h', 'w+') as f:
        f.write(templ.render(parser=ctx))

    # generate C code
    templ = env.get_template('parser.tmpl.c')
    with open(pkg_path / f'parser_{ctx["name"]}.c', 'w+') as f:
        f.write(templ.render(parser=ctx))

    # generate Python code
    templ = env.get_template('grammar_wrapper.tmpl.py')
    with open(pkg_path / f'grammar_{ctx["name"]}.py', 'w+') as f:
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
        ffibuilder.cdef(f'extern "Python" uint8_t {ext_decl}(parser_t *);')
        source_txt += f'static uint8_t {ext_decl}(parser_t *);\n'
        source_txt += f"uint8_t {ext_decl}_link(parser_t *p)" + " { return " + ext_decl + "(p); }\n"
    
    # TODO: must generate it for given grammar
    ffibuilder.set_source("lib_" + ctx['name'], source_txt, sources=[f'parser_{ctx["name"]}.c'])

    # Makefile features
    print(f"{pformat(vars(ffibuilder))}")
    for it in ffibuilder._assigned_source[3]['sources']:
        print(f"SOURCE {it}")
    ffibuilder.compile(tmpdir=pkg_path, verbose=True)
