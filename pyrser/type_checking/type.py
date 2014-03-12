# type for type checking
from pyrser import fmt
from pyrser.type_checking.scope import *


class Type(Scope):
    """
    A Type is a named scope similar to ADT (Abstract Data Type).
    So we have an member variables (ordered) that represent internal state.
    Member functions (work on an instance of type,
    depend of the language ref/or not).
    Non member variables/functions/valuess as in a scope.
    """

    def __init__(self, name: str, sig: [Signature]=None):
        super().__init__(name)

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
