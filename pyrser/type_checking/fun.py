# val for type checking (literal or ENUM style)
from pyrser import fmt
from pyrser.type_checking.signature import *


class Fun(Signature):
    """
    Describe a function signature for the language
    """

    def __init__(self, name: str, tret: str, tparams: list=None, variadic=None):
        if tparams is not None and not isinstance(tparams, list):
            raise TypeError("Fun's parameter list must be a list")
        super().__init__(name)
        if not isinstance(tret, TypeName):
            tret = TypeName(tret)
        self.tret = tret
        self.variadic = variadic
        self.tparams = None
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
        if self.tparams is not None:
            tparams = list(self.tparams)
        if self.variadic:
            tparams.append('...')
        params = '(' + ", ".join(tparams) + ')'
        txt.lsdata.append(': ' + params)
        txt.lsdata.append('-> ' + self.tret)
        return txt

    def internal_name(self):
        """
        Return the unique internal name
        """
        unq = super().internal_name()
        if self.tparams is not None:
            unq += "_" + "_".join(self.tparams)
        if self.tret is not None:
            unq += "_" + self.tret
        return unq

