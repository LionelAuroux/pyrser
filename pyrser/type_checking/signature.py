# basically function signature, but base class for many features
import weakref
from pyrser import fmt
from pyrser.type_checking.symbol import *
from pyrser.type_checking.type_name import *


class Signature(Symbol):
    """
    Describe a function or variable signature for the language
    """

    def __init__(self, name: str, tret: str, tparams: list=None,
                 variadic=None):
        super().__init__(name)
        if not isinstance(tret, TypeName):
            tret = TypeName(tret)
        self.tret = tret
        self.variadic = variadic
        if tparams is not None and len(tparams) > 0:
            self.tparams = []
            for p in tparams:
                if not isinstance(p, TypeName):
                    p = TypeName(p)
                self.tparams.append(p)

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
        if hasattr(self, 'tparams'):
            tparams = list(self.tparams)
        if self.variadic:
            tparams.append('...')
        params = '(' + ", ".join(tparams) + ')'
        txt.lsdata.append(': ' + params)
        txt.lsdata.append('-> ' + self.tret)
        return txt

    def __str__(self):
        return str(self.to_fmt())

    def is_var(self):
        return not hasattr(self, 'tparams')

    def is_fun(self):
        return hasattr(self, 'tparams')
