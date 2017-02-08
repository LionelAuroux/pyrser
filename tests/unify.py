import unittest

### Type Expr component

class TypeExprComponent(list):
    contains = None
    def __init__(self, *deflist):
        for t in deflist:
            if type(t).__name__ not in self.contains:
                raise TypeError("%s can't be put in %s" % (type(t), type(self)))
        list.__init__(self, deflist)

    @property
    def reprlist(self):
        r = []
        for it in self:
            t = str(it)
            if isinstance(it, list) and type(self) is not Overload and len(it) > 1:
                t = '(' + t + ')'
            r.append(t)
        return r

class Define:
    def __init__(self, name: str, type_def: TypeExprComponent):
        self.name = name
        self.type_def = type_def

    def __str__(self) -> str:
        return "%s: %s" % (self.name, self.type_def)

class Overload(TypeExprComponent):
    contains = {'Fun', 'str'}

    def __str__(self) -> str:
        return "\n& ".join(self.reprlist)

class Fun(TypeExprComponent):
    contains = {'Union', 'Tuple', 'str'}
    def __str__(self) -> str:
        return " -> ".join(reversed(self.reprlist))

class Union(TypeExprComponent):
    contains = {'Union', 'str'}
    def __str__(self) -> str:
        return " | ".join(self.reprlist)

class Tuple(TypeExprComponent):
    contains = {'Fun', 'Union', 'Tuple', 'str'}
    def __str__(self) -> str:
        return ", ".join(self.reprlist)

########### TODO voir pour Binding
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
# TODO:  TypeVar = ?1 type à instancier
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
        """Pretty Print Test"""
        d = Overload("t1", "t2")
        self.assertEqual(str(d), "t1\n& t2")
        d = Fun("t1", "t2")
        self.assertEqual(str(d), "t2 -> t1")
        d = Fun("t1", "t2")
        self.assertEqual(str(d), "t2 -> t1")
        d = Union("t1", "t2")
        self.assertEqual(str(d), "t1 | t2")
        d = Tuple("t1", "t2")
        self.assertEqual(str(d), "t1, t2")
        d = Fun('t3', Tuple("t1", "t2"))
        self.assertEqual(str(d), "(t1, t2) -> t3")

    def test_001(self):
        """Composition Test"""
        d = Overload(Fun("t1", Tuple("t2", "t3")),
            Fun("t4", Tuple("t2", "t4"))
            )
        self.assertEqual(str(d), "(t2, t3) -> t1\n& (t2, t4) -> t4")
        with self.assertRaises(TypeError):
            d = Overload(Overload("t2", "t3"))
        with self.assertRaises(TypeError):
            d = Overload(Union("t2", "t3"))
        with self.assertRaises(TypeError):
            d = Overload(Tuple("t2", "t3"))
        with self.assertRaises(TypeError):
            d = Fun(Overload("t2", "t3"))
        with self.assertRaises(TypeError):
            d = Fun(Fun("t2", "t3"))
        with self.assertRaises(TypeError):
            d = Union(Overload("t2", "t3"))
        with self.assertRaises(TypeError):
            d = Union(Fun("t2", "t3"))
        with self.assertRaises(TypeError):
            d = Tuple(Overload("t2", "t3"))

    def test_002(self):
        """Basic unification.
        We assume the Binding (link item to type definition is done.
        """
        def1 = Fun("t1", "t2")

