# val for type checking (literal or ENUM style)
from pyrser.type_system.signature import *
from pyrser.type_system.type_name import *


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
        if not isinstance(tret, TypeName):
            tret = TypeName(tret)
        self.tret = tret
        k = self.value + "$" + tret
        idx = 0
        if k not in Val.valuniq:
            Val.nvalues += 1
            Val.valuniq[k] = Val.nvalues
            idx = Val.nvalues
        else:
            idx = Val.valuniq[k]
        super().__init__('$' + str(idx))

    def internal_name(self):
        """
        Return the unique internal name
        """
        unq = super().internal_name()
        if self.tret is not None:
            unq += "_" + self.tret
        return unq

    def __str__(self) -> str:
        import pyrser.type_system.to_fmt
        return str(self.to_fmt())
