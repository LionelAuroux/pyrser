# fun for type checking (functions signatures)
from pyrser.type_system.signature import *
from pyrser.type_system.type_name import *


class Fun(Signature):
    """
    Describe a function signature for the language
    """

    def __init__(
        self,
        name: str,
        tret: str,
        tparams: list=None,
        variadic=None
    ):
        if tparams is not None and not isinstance(tparams, list):
            raise TypeError("Fun's parameter list must be a list")
        super().__init__(name)
        if not isinstance(tret, TypeName):
            tret = TypeName(tret)
        self.tret = tret
        self.variadic = variadic
        self.tparams = None
        if tparams is not None and len(tparams) > 0:
            self.tparams = []
            for p in tparams:
                if not isinstance(p, TypeName):
                    p = TypeName(p)
                self.tparams.append(p)

    @property
    def arity(self) -> int:
        return len(self.tparams)

    @property
    def return_type(self) -> str:
        return self.tret

    @property
    def this_type(self) -> str:
        return self.tparams[0]

    @property
    def is_polymorphic(self) -> bool:
        if self.tret.is_polymorphic:
            return True
        for p in self.tparams:
            if p.is_polymorphic:
                return True

    @property
    def is_fun(self) -> bool:
        return True

    def internal_name(self):
        """
        Return the unique internal name
        """
        unq = 'f_' + super().internal_name()
        if self.tparams is not None:
            unq += "_" + "_".join(self.tparams)
        if self.tret is not None:
            unq += "_" + self.tret
        return unq

    def __str__(self) -> str:
        import pyrser.type_system.to_fmt
        return str(self.to_fmt())
