# basically variables/functions signatures, but base class for many features
from pyrser.type_system.symbol import *


class Signature(Symbol):
    """
    Describe a function or variable signature for the language
    """

    def __init__(self, name: str):
        super().__init__(name)

    def __str__(self) -> str:
        import pyrser.type_system.to_fmt
        return str(self.to_fmt())
