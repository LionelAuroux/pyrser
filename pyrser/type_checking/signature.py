# basically function signature, but base class for many features
import weakref
from pyrser import fmt
from pyrser.type_checking.symbol import *
from pyrser.type_checking.type_name import *


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
