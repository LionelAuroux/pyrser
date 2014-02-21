# function or var signature
import weakref
from pyrser import fmt
from pyrser.type_checking.symbol import *


class Signature(Symbol):
    """
    Describe a function or variable signature for the language
    """

    def __init__(self, name: str, tret: str, *tparams):
        super().__init__(name)
        self.tret = tret
        if len(tparams) > 0:
            self.tparams = tparams

    def to_fmt(self):
        """
        Return an Fmt representation for pretty-printing
        """
        params = ""
        txt = fmt.sep(" ", ['var'])
        name = self.show_name()
        if name != "":
            txt.lsdata.append(name)
        if hasattr(self, 'tparams'):
            params = '(' + ", ".join(self.tparams) + ')'
            txt.lsdata[0] = 'fun'
            txt.lsdata.append(': ' + params)
            txt.lsdata.append('-> ' + self.tret)
        else:
            txt.lsdata.append(': ' + self.tret)
        return txt

    def __str__(self):
        return str(self.to_fmt())

    def is_var(self):
        return not hasattr(self, 'tparams')

    def is_fun(self):
        return hasattr(self, 'tparams')
