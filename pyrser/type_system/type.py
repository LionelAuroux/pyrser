# type for type checking
from pyrser.type_system.scope import *
from pyrser.type_system.type_name import *


class Type(Scope):
    """
    A Type is a named scope similar to ADT (Abstract Data Type).
    So we have member variables (ordered) that represent internal state.
    Member functions (work on an instance of type,
    depend of the language ref/or not).
    Non member variables/functions/values as in a scope.
    """

    def __str__(self) -> str:
        import pyrser.type_system.to_fmt
        return str(self.to_fmt())

    def __init__(self, name: str, sig: [Signature]=None):
        super().__init__(TypeName(name))

    @property
    def type_name(self) -> TypeName:
        return self.name
