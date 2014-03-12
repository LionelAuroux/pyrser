# val for type checking (literal or ENUM style)
from pyrser import fmt
from pyrser.type_checking.signature import *


class Val(Signature):
    """
    Describe a value signature for the language
    """
    nvalues = 0
    valuniq = dict()

    def __init__(self, value, tret: str):
        if not isinstance(value, str):
            value = str(value)
        self.value = value
        self.tret = tret
        k = self.value + "$" + tret
        idx = 0
        if k not in Val.valuniq:
            Val.nvalues += 1
            Val.valuniq[k] = Val.nvalues
            idx = Val.nvalues
        else:
            idx = Val.valuniq[k]
        super().__init__('$' + str(idx), tret)

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

    def internal_name(self):
        """
        Return the unique internal name
        """
        unq = "_".join(self.get_scope_names())
        if hasattr(self, 'tret'):
            unq += "_" + self.tret
        return unq
