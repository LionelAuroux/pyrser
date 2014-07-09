# This module is the STUB for converting grammar into a Cython module
import os
import subprocess
import shutil
from string import Template
from pyrser.codegen.c import template_cython
from pyrser import meta
from pyrser import fmt
from pyrser import parsing
from pyrser.parsing import functors
from pyrser import grammar
from pyrser.passes import to_yml

tpl_python = Template(template_cython.c_python)
tpl_python_attr = Template(template_cython.c_python_attr)
tpl_setup = Template(template_cython.c_setup)
tpl_pyx = Template(template_cython.c_pyx)
tpl_pyx_rules = Template(template_cython.c_pyx_rules)
tpl_pxd = Template(template_cython.c_pxd)
tpl_pproto = Template(template_cython.c_pproto)
# C Stub Templates
tpl_header = Template(template_cython.c_header)
tpl_file = Template(template_cython.c_file)
tpl_cproto = Template(template_cython.c_cproto)
tpl_function = Template(template_cython.c_function)
# Primitives Alt/Seq/Rep
tpl_seqhead = Template(template_cython.c_seqhead)
tpl_seqfoot = Template(template_cython.c_seqfoot)
tpl_seq = Template(template_cython.c_seq)
tpl_althead = Template(template_cython.c_althead)
tpl_altfoot = Template(template_cython.c_altfoot)
tpl_alt = Template(template_cython.c_alt)
tpl_rep0n = Template(template_cython.c_rep0n)
tpl_rep1n = Template(template_cython.c_rep1n)
tpl_repopt = Template(template_cython.c_repopt)
# Primitives !,~,!!,->
tpl_neg = Template(template_cython.c_neg)
tpl_complement = Template(template_cython.c_complement)
tpl_lookahead = Template(template_cython.c_lookahead)
tpl_until = Template(template_cython.c_until)
# Primitives '', ..., ""
tpl_char = Template(template_cython.c_char)
tpl_range = Template(template_cython.c_range)
tpl_text = Template(template_cython.c_text)

def genImport(g: grammar.Grammar, indir='.') -> 'module':
    generate(p, indir)
    lspkg = []
    for p in indir.split(os.sep):
        if p[0] != '.':
            lspkg.append(p)
    lspkg.append(type(p).__name__.lower())
    pkg_name = '.'.join(lspkg)
    return importlib.import_module(pkg_name)

# Use the Cython stub to translate grammar g into C/Python in the output directory p
def generate(g: grammar.Grammar, indir='.', keep_tmp=False):
    ctype_name = g.__class__.__name__
    p = indir + os.sep + ctype_name + '_generated'
    cstub = g.to_cython(ctype_name)
    os.makedirs(p, exist_ok=True)
    with open(p + os.sep + 'setup.py', 'w') as f:
        f.write(str(cstub.setup))
    with open(p + os.sep + ctype_name + ".pyx", 'w') as f:
        f.write(str(cstub.pyx))
    with open(p + os.sep + ctype_name + "_internal.pxd", 'w') as f:
        f.write(str(cstub.pxd))
    with open(p + os.sep + ctype_name + "_internal.h", 'w') as f:
        f.write(str(cstub.cheader))
    with open(p + os.sep + ctype_name + "_internal.c", 'w') as f:
        f.write(str(cstub.csource))
    tmpdir = os.getcwd()
    os.chdir(p)
    subprocess.check_call(['python3', 'setup.py', 'build'])
    subprocess.check_call(['python3', 'setup.py', 'install_lib', '-d', '..'])
    os.chdir(tmpdir)
    if not keep_tmp:
        shutil.rmtree(p)
    with open(indir + os.sep + ctype_name.lower() + '.py', 'w') as f:
        f.write(str(cstub.psource))


class CStub:
    def __init__(self):
        self.psource = None
        self.setup = None
        self.pyx = None
        self.pxd = None
        self.cheader = None
        self.csource = None

class GenState:
    def __init__(self):
        self._lvlids = [0]
        self._lvlid = 0
        self._errids = [0]
        self._errid = 0

    def newScopeError(self):
        self._lvlid += 1
        self._lvlids.append(self._lvlid)
        self._errid += 1
        self._errids.append(self._errid)

    def popScopeError(self):
        self._lvlids.pop()
        self._errids.pop()

    def newScopeAlt(self):
        self._lvlids.append(self.lvlid)
        self._errid += 1
        self._errids.append(self._errid)

    def popScopeAlt(self):
        self._lvlids.pop()
        self._errids.pop()

    @property
    def lvlid(self):
        if len(self._lvlids) > 1:
            return self._lvlids[-1]
        return 0

    @property
    def outid(self):
        return self._lvlids[-2]

    @property
    def errid(self):
        if len(self._errids) > 1:
            return self._errids[-1]
        return 0

    @property
    def outerrid(self):
        return self._errids[-2]

    def __repr__(self):
        txt = "Lvl: [\n"
        for l in self._lvlids:
            txt += str(l) + ",\n"
        txt += "]\nErr:[\n"
        for e in self._errids:
            txt += str(e) + ",\n"
        txt += "]\n"
        return txt

@meta.add_method(parsing.Parser)
def to_cython(self, ctype_name: str) -> CStub:
    cstub = CStub()
    # SETUP GENERATION
    cstub.setup = fmt.end('', [])
    cstub.setup.lsdata.append(tpl_setup.substitute(
        ctn=ctype_name,
    ))
    # CSOURCE GENERATION
    pyattr = fmt.end('', [])
    pyxprotos = fmt.end('', [])
    pprotos = fmt.end('', [])
    cprotos = fmt.end('', [])
    gram = fmt.end('//---\n', [])
    gram.lsdata.append(tpl_file.substitute(ctn=ctype_name))
    for k, v in self.__class__._rules.items():
        try:
            if isinstance(v, parsing.Functor):
                genstate = GenState()
                fun_name = k.replace('.', '_')
                #
                if not isinstance(v, functors.Seq):
                    v = functors.Seq(v)
                rule_code = v.to_cython(genstate)
                content = tpl_function.substitute(
                    ctn=ctype_name,
                    rule=fun_name,
                    code=fmt.tab([rule_code]),
                    lvlid=genstate.lvlid,
                    errid=genstate.errid
                )
                rule = fmt.sep(
                               '\n',
                               [
                                "//--- %s" % k,
                                content
                               ]
                )
                pyattr.lsdata.append(tpl_python_attr.substitute(
                    rule=fun_name
                ))
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
                gram.lsdata.append(rule)
        except:
            #print("Can't Transform %s = %s" % (k, to_yml.to_yml(v)))
            pass
    cstub.csource = gram
    # PYTHON GENERATION
    cstub.psource = fmt.end('', [])
    cstub.psource.lsdata.append(tpl_python.substitute(
        ctn=ctype_name,
        rules_attr=str(pyattr)
    ))
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

@meta.add_method(functors.SkipIgnore)
def to_cython(self, genstate) -> fmt.indentable:
    """
    TODO: A quite important part of C transform... rethink directive/decoration/etc...
    """
    return '\n'

@meta.add_method(functors.Rule)
def to_cython(self, genstate) -> fmt.indentable:
    return '\n'

@meta.add_method(functors.Hook)
def to_cython(self, genstate) -> fmt.indentable:
    return '\n'

@meta.add_method(functors.PeekText)
def to_cython(self, genstate) -> fmt.indentable:
    raise TypeError("functors.PeekText don't have to be in a PTree for Cythonization")

@meta.add_method(functors.PeekChar)
def to_cython(self, genstate) -> fmt.indentable:
    raise TypeError("functors.PeekChar don't have to be in a PTree for Cythonization")

@meta.add_method(functors.Range)
def to_cython(self, genstate) -> fmt.indentable:
    return tpl_range.substitute(
        char_begin=self.begin,
        char_end=self.end,
        lvlid=genstate.lvlid,
        errid=genstate.errid
    )

@meta.add_method(functors.Text)
def to_cython(self, genstate) -> fmt.indentable:
    return tpl_text.substitute(
        text=self.text,
        lvlid=genstate.lvlid,
        errid=genstate.errid
    )

@meta.add_method(functors.Char)
def to_cython(self, genstate) -> fmt.indentable:
    return tpl_char.substitute(
        char=self.char,
        lvlid=genstate.lvlid,
        errid=genstate.errid
    )

@meta.add_method(functors.Scope)
def to_cython(self, genstate) -> fmt.indentable:
    raise TypeError("functors.Scope don't have to be in a PTree for Cythonization")

@meta.add_method(functors.Directive)
def to_cython(self, genstate) -> fmt.indentable:
    return '\n'

@meta.add_method(functors.Capture)
def to_cython(self, genstate) -> fmt.indentable:
    return '\n'

@meta.add_method(functors.DeclNode)
def to_cython(self, genstate) -> fmt.indentable:
    return '\n'

@meta.add_method(functors.Bind)
def to_cython(self, genstate) -> fmt.indentable:
    return '\n'

@meta.add_method(functors.Error)
def to_cython(self, genstate) -> fmt.indentable:
    raise TypeError("functors.Error don't have to be in a PTree for Cythonization")

# concatenate all IR of a seq
@meta.add_method(functors.Seq)
def to_cython(self, genstate) -> fmt.indentable:
    seqs = fmt.tab([])
    genstate.newScopeError()
    seqs.lsdata.append(tpl_seqhead.substitute(
        lvlid=genstate.lvlid,
        outid=genstate.outid
    ))
    for s in self.ptlist:
        content = tpl_seq.substitute(code=s.to_cython(genstate))
        seqs.lsdata.append(content)
    seqs.lsdata.append(tpl_seqfoot.substitute(
        lvlid=genstate.lvlid,
        outid=genstate.outid,
        errid=genstate.errid,
        outerrid=genstate.outerrid
    ))
    genstate.popScopeError()
    return seqs

@meta.add_method(functors.Alt)
def to_cython(self, genstate) -> fmt.indentable:
    alts = fmt.tab([])
    genstate.newScopeError()
    alts.lsdata.append(tpl_althead.substitute(
        lvlid=genstate.lvlid,
        outid=genstate.outid
    ))
    for s in self.ptlist:
        if not isinstance(s, functors.Seq):
            s = functors.Seq(s)
        genstate.newScopeAlt()
        content = tpl_alt.substitute(
            code=s.to_cython(genstate),
            lvlid=genstate.lvlid,
            outid=genstate.outid,
            errid=genstate.errid,
            outerrid=genstate.outerrid
        )
        alts.lsdata.append(content)
        genstate.popScopeAlt()
    alts.lsdata.append(tpl_altfoot.substitute(
        lvlid=genstate.lvlid,
        outid=genstate.outid,
        errid=genstate.errid,
        outerrid=genstate.outerrid
    ))
    genstate.popScopeError()
    return alts

@meta.add_method(functors.Complement)
def to_cython(self, genstate) -> fmt.indentable:
    rule = self.pt
    if not isinstance(rule, functors.Seq):
        rule = functors.Seq(rule)
    genstate.newScopeError()
    source = fmt.tab([rule.to_cython(genstate)])
    res = tpl_complement.substitute(
        code=self.pt.to_cython(genstate),
        lvlid=genstate.lvlid,
        outid=genstate.outid,
        errid=genstate.errid,
        outerrid=genstate.outerrid
    )
    genstate.popScopeError()
    return res

@meta.add_method(functors.LookAhead)
def to_cython(self, genstate) -> fmt.indentable:
    rule = self.pt
    if not isinstance(rule, functors.Seq):
        rule = functors.Seq(rule)
    genstate.newScopeError()
    source = fmt.tab([rule.to_cython(genstate)])
    res = tpl_lookahead.substitute(
        code=self.pt.to_cython(genstate),
        lvlid=genstate.lvlid,
        outid=genstate.outid,
        errid=genstate.errid,
        outerrid=genstate.outerrid
    )
    genstate.popScopeError()
    return res

@meta.add_method(functors.Neg)
def to_cython(self, genstate) -> fmt.indentable:
    rule = self.pt
    if not isinstance(rule, functors.Seq):
        rule = functors.Seq(rule)
    genstate.newScopeError()
    source = fmt.tab([rule.to_cython(genstate)])
    res = tpl_neg.substitute(
        code=self.pt.to_cython(genstate),
        lvlid=genstate.lvlid,
        outid=genstate.outid,
        errid=genstate.errid,
        outerrid=genstate.outerrid
    )
    genstate.popScopeError()
    return res

@meta.add_method(functors.Until)
def to_cython(self, genstate) -> fmt.indentable:
    rule = self.pt
    if not isinstance(rule, functors.Seq):
        rule = functors.Seq(rule)
    genstate.newScopeError()
    source = fmt.tab([rule.to_cython(genstate)])
    res = tpl_until.substitute(
        code=self.pt.to_cython(genstate),
        lvlid=genstate.lvlid,
        outid=genstate.outid,
        errid=genstate.errid,
        outerrid=genstate.outerrid
    )
    genstate.popScopeError()
    return res

@meta.add_method(functors.UntilChar)
def to_cython(self, genstate) -> fmt.indentable:
    raise TypeError("functors.UntilChar don't have to be in a PTree for Cythonization")

@meta.add_method(functors.RepOptional)
def to_cython(self, genstate) -> fmt.indentable:
    repn = self.pt
    if not isinstance(repn, functors.Seq):
        repn = functors.Seq(repn)
    genstate.newScopeError()
    source = fmt.tab([repn.to_cython(genstate)])
    res = tpl_repopt.substitute(
        code=self.pt.to_cython(genstate),
        lvlid=genstate.lvlid,
        outid=genstate.outid,
        errid=genstate.errid,
    )
    genstate.popScopeError()
    return res

@meta.add_method(functors.Rep0N)
def to_cython(self, genstate) -> fmt.indentable:
    repn = self.pt
    if not isinstance(repn, functors.Seq):
        repn = functors.Seq(repn)
    genstate.newScopeError()
    source = fmt.tab([repn.to_cython(genstate)])
    res = tpl_rep0n.substitute(
        code=str(source),
        lvlid=genstate.lvlid,
        outid=genstate.outid,
        errid=genstate.errid,
        outerrid=genstate.outerrid
    )
    genstate.popScopeError()
    return res

@meta.add_method(functors.Rep1N)
def to_cython(self, genstate) -> fmt.indentable:
    repn = self.pt
    if not isinstance(repn, functors.Seq):
        repn = functors.Seq(repn)
    genstate.newScopeError()
    source = fmt.tab([repn.to_cython(genstate)])
    res = tpl_rep1n.substitute(
        code=str(source),
        lvlid=genstate.lvlid,
        outid=genstate.outid,
        errid=genstate.errid,
        outerrid=genstate.outerrid
    )
    genstate.popScopeError()
    return res
