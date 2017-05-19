# var for type checking (variables)
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

    @property
    def is_var(self) -> bool:
        return True

    def internal_name(self):
        """
        Return the unique internal name
        """
        unq = 'v_' + super().internal_name()
        if self.tret is not None:
            unq += "_" + self.tret
        return unq

    def __str__(self) -> str:
        import pyrser.type_system.to_fmt
        return str(self.to_fmt())
