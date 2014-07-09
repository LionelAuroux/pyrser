# tuple handling
from pyrser import fmt
from pyrser.type_system.signature import *


class Tuple(list):
    """
    A tuple is just a list of signature.
    """
    def __init__(self, sig: [Signature]=None):
        self._lsig = []
        if sig is not None:
            if isinstance(sig, Signature):
                self.add(sig)
            elif len(sig) > 0:
                for s in sig:
                    self.add(s)

    def add(self, sig: Signature):
        self._lsig.append(sig)

    def to_fmt(self) -> fmt.indentable:
        """
        Return an Fmt representation for pretty-printing
        """
        lsb = []
        if len(self._lsig) > 0:
            for s in self._lsig:
                lsb.append(s.to_fmt())
        block = fmt.block("(", ")", fmt.sep(', ', lsb))
        qual = "tuple"
        txt = fmt.sep("", [qual, block])
        return txt

    def __repr__(self) -> str:
        """
        Internal representation
        """
        return repr(self._lsig)

    def __str__(self) -> str:
        """
        Usefull representation
        """
        return str(self.to_fmt())
