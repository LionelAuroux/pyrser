# IR allow to represent algorithmic bricks of PEG parsing

class IR:
    """ Base class for Internal Representation of algorithmic bricks. """


class Grammar(IR):
    """Abstraction of a whole grammar."""

    def __init__(self, name: str):
        self.name = name
        self.rules = []

class Rule(IR):
    """Abstraction of a target function. """
    
    def __init__(self, name: str):
        self.name = name
        self.block = None

class Block(IR):
    
    def __init__(self, lsexpr: list):
        if not isinstance(lsexpr, list):
            raise TypeError("Take only a list")
        self.lsexpr = lsexpr

class CallRule(IR):
    pass


class GetC(IR):
    pass

class IncPos(IR):
    pass

class EqualBlock(IR):
    
    def __init__(self, v: str):
        self.value = v
        self.block = None

class RangeBlock(IR):
    pass

class WhileEofBlock(IR):
    """ """
    pass


class ReturnOnEof(IR):
    """If we reach the EOF, we abort parsing directly."""
    pass


class SaveCtx(IR):
    """Temporary save the current parsing context."""
    pass

class RestoreCtx(IR):
    """Restore previous parsing context."""
    pass

class ValidateCtx(IR):
    """Validate current parsing context."""
    pass

class Return(IR):
    """Abstraction of a return statement. return the last boolean state."""
    pass
