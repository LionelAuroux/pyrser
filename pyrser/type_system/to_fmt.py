# fmt classes
from pyrser import fmt, meta

from pyrser.type_system.scope import Scope
from pyrser.type_system.type import Type
from pyrser.type_system.evalctx import EvalCtx
from pyrser.type_system.translator import Translator
from pyrser.type_system.translator import MapTargetTranslate
from pyrser.type_system.translator import MapSourceTranslate
from pyrser.type_system.signature import Signature
from pyrser.type_system.val import Val
from pyrser.type_system.var import Var
from pyrser.type_system.fun import Fun


# ======== PRETTY PRINTING ========

@meta.add_method(Scope)
def to_fmt(self) -> fmt.indentable:
    """
    Return an Fmt representation for pretty-printing
    """
    qual = "scope"
    txt = fmt.sep(" ", [qual])
    name = self.show_name()
    if name != "":
        txt.lsdata.append(name)
    if len(self._hsig) > 0 or len(self.mapTypeTranslate) > 0:
        lsb = []
        if len(self.mapTypeTranslate) > 0:
            lsb.append("translate:\n")
            lsb.append(fmt.end("\n", self.mapTypeTranslate.to_fmt()))
        for k in sorted(self._hsig.keys()):
            s = self._hsig[k]
            lsb.append(fmt.end("\n", [s.to_fmt()]))
        block = fmt.block(":\n", "", fmt.tab(lsb))
        txt.lsdata.append(block)
    return txt


@meta.add_method(Type)
def to_fmt(self) -> fmt.indentable:
    """
    Return an Fmt representation for pretty-printing
    """
    qual = "type"
    txt = fmt.sep(" ", [qual])
    txt.lsdata.append(self.show_name())
    if hasattr(self, '_hsig') and len(self._hsig) > 0:
        lsb = []
        for k in sorted(self._hsig.keys()):
            s = self._hsig[k]
            lsb.append(fmt.end("\n", [s.to_fmt()]))
        block = fmt.block(":\n", "", fmt.tab(lsb))
        txt.lsdata.append(block)
    return txt


@meta.add_method(EvalCtx)
def to_fmt(self):
    """
    Return an Fmt representation for pretty-printing
    """
    qual = "evalctx"
    lseval = []
    block = fmt.block(":\n", "", fmt.tab(lseval))
    txt = fmt.sep(" ", [qual, block])
    lseval.append(self._sig.to_fmt())
    if len(self.resolution) > 0:
        lsb = []
        for k in sorted(self.resolution.keys()):
            s = self.resolution[k]
            if s is not None:
                lsb.append(
                    fmt.end(
                        "\n",
                        ["'%s': %s (%s)" % (k, s, s().show_name())]
                    )
                )
            else:
                lsb.append(fmt.end("\n", ["'%s': Unresolved" % (k)]))
        if self._translate_to is not None:
            lsb.append("use translator:")
            lsb.append(self._translate_to.to_fmt())
        if self._variadic_types is not None:
            lsb.append("variadic types:\n")
            arity = self._sig.arity
            for t in self._variadic_types:
                lsb.append("[%d] : %s\n" % (arity, t))
                arity += 1
        lseval.append(fmt.block("\nresolution :\n", "", fmt.tab(lsb)))
    return txt


@meta.add_method(Translator)
def to_fmt(self, with_from=False) -> fmt.indentable:
    """
    Return a Fmt representation of Translator for pretty-printing
    """
    txt = fmt.sep("\n", [
        fmt.sep(
            " ",
            [
                self._type_source,
                "to",
                self._type_target,
                '=',
                self._fun.to_fmt()
            ]
        ),
        self._notify.get_content(with_from)
    ])
    return txt


@meta.add_method(MapTargetTranslate)
def to_fmt(self, with_from=False) -> fmt.indentable:
    txt = fmt.block('{\n', '\n}', [])
    items = fmt.sep('\n---\n', [])
    for k in sorted(self._internal.keys()):
        items.lsdata.append(
            fmt.sep(': ', [
                k,
                fmt.tab([self._internal[k].to_fmt(with_from)])
                ])
        )
    txt.lsdata.append(fmt.tab([items]))
    return txt


@meta.add_method(MapSourceTranslate)
def to_fmt(self, with_from=False) -> fmt.indentable:
    txt = fmt.block('{\n', '\n}', [])
    items = fmt.sep('\n---\n', [])
    for k in sorted(self._internal.keys()):
        items.lsdata.append(
            fmt.sep(': ', [
                k,
                fmt.tab([self._internal[k].to_fmt(with_from)])
                ])
        )
    txt.lsdata.append(fmt.tab([items]))
    return txt


@meta.add_method(Signature)
def to_fmt(self):
    raise TypeError("Signature.to_fmt must be redefined")


@meta.add_method(Val)
def to_fmt(self):
    """
    Return an Fmt representation for pretty-printing
    """
    params = ""
    txt = fmt.sep(" ", ['val'])
    name = self.show_name()
    if name != "":
        txt.lsdata.append(name)
    txt.lsdata.append('(%s)' % self.value)
    txt.lsdata.append(': ' + self.tret)
    return txt


@meta.add_method(Var)
def to_fmt(self):
    """
    Return an Fmt representation for pretty-printing
    """
    params = ""
    txt = fmt.sep(" ", ['var'])
    name = self.show_name()
    if name != "":
        txt.lsdata.append(name)
    txt.lsdata.append(': ' + self.tret)
    return txt


@meta.add_method(Fun)
def to_fmt(self):
    """
    Return an Fmt representation for pretty-printing
    """
    params = ""
    txt = fmt.sep(" ", ['fun'])
    name = self.show_name()
    if name != "":
        txt.lsdata.append(name)
    tparams = []
    if self.tparams is not None:
        tparams = list(self.tparams)
    if self.variadic:
        tparams.append('...')
    params = '(' + ", ".join(tparams) + ')'
    txt.lsdata.append(': ' + params)
    txt.lsdata.append('-> ' + self.tret)
    return txt
