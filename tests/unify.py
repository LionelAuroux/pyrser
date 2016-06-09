import unittest

# symbol
class Symbol:
    """
    $N nom d'un symbole
    """
    pass

# type concret
class TypeConcret:
    """
    int | bool etc...
    """
    pass

# type template
class TypeVar:
    """
    ?A type variable ou placeholder
    """
    pass

# type id
class TypeId:
    """
    tA type id ou alias
    """
    pass

# fun
class TypeFun:
    """
    () -> ()
    """
    pass

# mapping
class TypeMap:
    """
    {k: v} k TypeId ou Symbol pour un v quelconque
    context local
    """
    pass

class Unifying_Test(unittest.TestCase):

    def test_000(self):
        """Unification test"""
