# This module is for converting functors into a Cython module
# for easy target language transformation
import os
from string import Template
from pyrser.codegen.c import template_cython
from pyrser import meta
from pyrser import fmt
from pyrser import parsing
from pyrser import grammar

tpl_setup = Template(template_cython.c_setup)
tpl_pyx = Template(template_cython.c_pyx)
tpl_pyx_rules = Template(template_cython.c_pyx_rules)
tpl_pxd = Template(template_cython.c_pxd)
tpl_header = Template(template_cython.c_header)
tpl_file = Template(template_cython.c_file)
tpl_pproto = Template(template_cython.c_pproto)
tpl_cproto = Template(template_cython.c_cproto)
tpl_function = Template(template_cython.c_function)
tpl_char = Template(template_cython.c_char)
tpl_althead = Template(template_cython.c_althead)
tpl_altfoot = Template(template_cython.c_altfoot)
tpl_alt = Template(template_cython.c_alt)


# Use the Cython stub to translate grammar g into C/Python in the output directory p
def generate(g: grammar.Grammar, p: str):
    ctype_name = 'Parser_' + g.__class__.__name__
    cstub = g.to_cython(ctype_name)
    print(str(cstub.setup))
    print(str(cstub.pyx))
    print(str(cstub.pxd))
    print(str(cstub.cheader))
    print(str(cstub.csource))
    os.makedirs(p, exist_ok=True)
    with open(p + '/setup.py', 'w') as f:
        f.write(str(cstub.setup))
    with open(p + '/' + ctype_name + ".pyx", 'w') as f:
        f.write(str(cstub.pyx))
    with open(p + '/' + ctype_name + "_internal.pxd", 'w') as f:
        f.write(str(cstub.pxd))
    with open(p + '/' + ctype_name + "_internal.h", 'w') as f:
        f.write(str(cstub.cheader))
    with open(p + '/' + ctype_name + "_internal.c", 'w') as f:
        f.write(str(cstub.csource))


class CStub:
    def __init__(self):
        self.setup = None
        self.pyx = None
        self.pxd = None
        self.cheader = None
        self.csource = None

class GenState:
    def __init__(self):
        # ID of the alternative
        self.stack = None

@meta.add_method(parsing.Parser)
def to_cython(self, ctype_name: str) -> CStub:
    genstate = GenState()
    cstub = CStub()
    # SETUP GENERATION
    cstub.setup = fmt.end('', [])
    cstub.setup.lsdata.append(tpl_setup.substitute(
        ctn=ctype_name,
    ))
    # CSOURCE GENERATION
    pyxprotos = fmt.end('', [])
    pprotos = fmt.end('', [])
    cprotos = fmt.end('', [])
    gram = fmt.end('//---\n', [])
    gram.lsdata.append(tpl_file.substitute(ctn=ctype_name))
    for k, v in self.__class__._rules.items():
        if isinstance(v, parsing.Functor):
            fun_name = k.replace('.', '_')
            pprotos.lsdata.append(tpl_pproto.substitute(
                ctn=ctype_name,
                rule=fun_name
            ))
            cprotos.lsdata.append(tpl_cproto.substitute(
                ctn=ctype_name,
                rule=fun_name
            ))
            pyxprotos.lsdata.append(tpl_pyx_rules.substitute(
                ctn=ctype_name,
                rule=fun_name
            ))
            genstate.stack = [{'altid': 0, 'nextid': id(v)}]
            rule_code = v.to_cython(genstate)
            content = tpl_function.substitute(
                ctn=ctype_name,
                rule=fun_name,
                code=rule_code,
                altid=genstate.stack[-1]['altid'],
                nextid=genstate.stack[-1]['nextid']
            )
            rule = fmt.sep(
                           '\n',
                           [
                            "//--- %s" % k,
                            content
                           ]
            )
            gram.lsdata.append(rule)
    cstub.csource = gram
    # CHEADER GENERATION
    cstub.cheader = fmt.end('', [])
    cstub.cheader.lsdata.append(tpl_header.substitute(
        ctn=ctype_name,
        cfunctions_proto=str(cprotos)
    ))
    # PXD GENERATION
    cstub.pxd = fmt.end('', [])
    cstub.pxd.lsdata.append(tpl_pxd.substitute(
        ctn=ctype_name,
        pfunctions_proto=str(pprotos)
    ))
    # PYX GENERATION
    cstub.pyx = fmt.end('', [])
    cstub.pyx.lsdata.append(tpl_pyx.substitute(
        ctn=ctype_name,
        rfunctions_proto=str(pyxprotos)
    ))
    return cstub

@meta.add_method(parsing.Rule)
def to_cython(self, genstate) -> fmt.indentable:
    return '\n'

@meta.add_method(parsing.Hook)
def to_cython(self, genstate) -> fmt.indentable:
    return '\n'

@meta.add_method(parsing.PeekText)
def to_cython(self, genstate) -> fmt.indentable:
    return '\n'

@meta.add_method(parsing.PeekChar)
def to_cython(self, genstate) -> fmt.indentable:
    return '\n'

@meta.add_method(parsing.Text)
def to_cython(self, genstate) -> fmt.indentable:
    return '\n'

@meta.add_method(parsing.Char)
def to_cython(self, genstate) -> fmt.indentable:
    return tpl_char.substitute(
        char=self.char,
        altid=genstate.stack[-1]['altid'],
        nextid=genstate.stack[-1]['nextid']
    )

@meta.add_method(parsing.Scope)
def to_cython(self, genstate) -> fmt.indentable:
    return '\n'

@meta.add_method(parsing.Directive)
def to_cython(self, genstate) -> fmt.indentable:
    return '\n'

@meta.add_method(parsing.Capture)
def to_cython(self, genstate) -> fmt.indentable:
    return '\n'

@meta.add_method(parsing.DeclNode)
def to_cython(self, genstate) -> fmt.indentable:
    return '\n'

@meta.add_method(parsing.Bind)
def to_cython(self, genstate) -> fmt.indentable:
    return '\n'

@meta.add_method(parsing.Error)
def to_cython(self, genstate) -> fmt.indentable:
    return '\n'

# concatenate all IR of a seq
@meta.add_method(parsing.Seq)
def to_cython(self, genstate) -> fmt.indentable:
    seqs = fmt.tab([])
    for s in self.ptlist:
        seqs.lsdata.append(s.to_cython(genstate))
    return seqs

@meta.add_method(parsing.Alt)
def to_cython(self, genstate) -> fmt.indentable:
    alts = fmt.tab([])
    alts.lsdata.append(tpl_althead.substitute(
        outid=genstate.stack[-1]['altid'],
        altid=genstate.stack[-1]['altid'] + 1,
    ))
    for s in self.ptlist:
        genstate.stack.append({'altid': len(genstate.stack), 'nextid': id(s)})
        content = tpl_alt.substitute(
            code=s.to_cython(genstate),
            altid=genstate.stack[-1]['altid'],
            outid=genstate.stack[-2]['altid'],
            nextid=genstate.stack[-1]['nextid'],
        )
        alts.lsdata.append(content)
        genstate.stack.pop()
    alts.lsdata.append(tpl_altfoot.substitute(
        outid=genstate.stack[-1]['altid'],
        altid=genstate.stack[-1]['altid'] + 1,
        nextid=genstate.stack[-1]['nextid']
    ))
    return alts

@meta.add_method(parsing.Neg)
def to_cython(self, genstate) -> fmt.indentable:
    return '\n'

@meta.add_method(parsing.Complement)
def to_cython(self, genstate) -> fmt.indentable:
    return '\n'

@meta.add_method(parsing.Until)
def to_cython(self, genstate) -> fmt.indentable:
    return '\n'

@meta.add_method(parsing.UntilChar)
def to_cython(self, genstate) -> fmt.indentable:
    return '\n'

@meta.add_method(parsing.LookAhead)
def to_cython(self, genstate) -> fmt.indentable:
    return '\n'

@meta.add_method(parsing.Neg)
def to_cython(self, genstate) -> fmt.indentable:
    return '\n'

@meta.add_method(parsing.RepOptional)
def to_cython(self, genstate) -> fmt.indentable:
    return '\n'

@meta.add_method(parsing.Rep0N)
def to_cython(self, genstate) -> fmt.indentable:
    return '\n'

@meta.add_method(parsing.Rep1N)
def to_cython(self, genstate) -> fmt.indentable:
    return '\n'
