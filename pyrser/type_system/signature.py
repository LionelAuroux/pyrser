# basically variables/functions signatures, but base class for many features
from pyrser.type_system.symbol import *


class Signature(Symbol):
    """
    Describe a function or variable signature for the language
    """
    def __init__(self, name: str):
        super().__init__(name)

    def to_fmt(self):
        raise TypeError("Signature.to_fmt must be redefined")

    def __str__(self):
        return str(self.to_fmt())
