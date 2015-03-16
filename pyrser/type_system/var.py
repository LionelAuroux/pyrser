# var for type checking (variables)
from pyrser import fmt
from pyrser.type_system.signature import *
from pyrser.type_system.type_name import *


class Var(Signature):
    """
    Describe a variable signature for the language
    """

    def __init__(self, name: str, tret: str):
        super().__init__(name)
        if not isinstance(tret, TypeName):
            tret = TypeName(tret)
        self.tret = tret

    @property
    def is_polymorphic(self) -> bool:
        return self.tret.is_polymorphic

    def internal_name(self):
        """
        Return the unique internal name
        """
        unq = super().internal_name()
        if self.tret is not None:
            unq += "_" + self.tret
        return unq
