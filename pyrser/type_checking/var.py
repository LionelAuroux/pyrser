# val for type checking (literal or ENUM style)
from pyrser import fmt
from pyrser.type_checking.signature import *


class Var(Signature):
    """
    Describe a variable signature for the language
    """

    def __init__(self, name: str, tret: str):
        super().__init__(name)
        if not isinstance(tret, TypeName):
            tret = TypeName(tret)
        self.tret = tret

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

    def internal_name(self):
        """
        Return the unique internal name
        """
        unq = super().internal_name()
        if self.tret is not None:
            unq += "_" + self.tret
        return unq
