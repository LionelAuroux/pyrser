import unittest
from pyrser.type_checking.signature import *
from pyrser.type_checking.set import *

class InternalType_Test(unittest.TestCase):
    def test_01_pp(self):
        var = Signature('var1', 'int')
        f1 = Signature('fun1', 'int', '')
        f2 = Signature('fun2', 'int', 'int')
        f3 = Signature('fun3', 'int', 'int', 'double')
        tenv = Set(None, [var, f1, f2, f3])
        self.assertEqual(str(var), "var var1 : int", "Bad pretty printing of type")
        self.assertEqual(str(f1), "fun fun1 : () -> int", "Bad pretty printing of type")
        self.assertEqual(str(f2), "fun fun2 : (int) -> int", "Bad pretty printing of type")
        self.assertEqual(str(f3), "fun fun3 : (int, double) -> int", "Bad pretty printing of type")
        self.assertEqual(str(tenv), """scope :
    fun fun1 : () -> int
    fun fun2 : (int) -> int
    fun fun3 : (int, double) -> int
    var var1 : int
""", "Bad pretty printing of type")

    def test_02_setop(self):
        var = Signature('var1', 'int')
        tenv = RawSet(var)
        self.assertIn(Signature('var1', 'int'), tenv, "Bad __contains__ in type_checking.Set")
        tenv.add(Signature('fun1', 'int', 'float' , 'char'))
        self.assertIn(Signature('fun1', 'int', 'float' , 'char'), tenv, "Bad __contains__ in type_checking.Set")
        ## inplace modification
        # work with any iterable
        tenv |= [Signature('fun2', 'int', 'int')]
        self.assertIn(Signature('fun2', 'int', 'int'), tenv, "Bad __contains__ in type_checking.Set")
        # work with any iterable
        tenv |= {Signature('fun3', 'int', 'int')}
        self.assertIn(Signature('fun3', 'int', 'int'), tenv, "Bad __contains__ in type_checking.Set")
        # retrieves past signature
        v = tenv.get(var.uniq_name())
        self.assertEqual(id(v), id(var), "Bad get in type_checking.Set")
        # intersection_update, only with Set
        tenv &= RawSet(Signature('var1', 'int'))
        v = tenv.get(var.uniq_name())
        self.assertNotEqual(id(v), id(var), "Bad &= in type_checking.Set")
        # difference_update, only with Set
        tenv |= [Signature('fun2', 'int', 'int'), Signature('fun3', 'char', 'double', 'float')]
        tenv -= RawSet(Signature('var1', 'int'))
        self.assertNotIn(Signature('var1', 'int'), tenv, "Bad -= in type_checking.Set")
        # symmetric_difference_update, only with Set
        tenv ^= RawSet(Signature('var2', 'double'), Signature('fun2', 'int', 'int'), Signature('fun4', 'plop', 'plip', 'ploum'))
        self.assertIn(Signature('fun4', 'plop', 'plip', 'ploum'), tenv, "Bad ^= in type_checking.Set")
        self.assertNotIn(Signature('fun2', 'int', 'int'), tenv, "Bad ^= in type_checking.Set")
        ## binary operation
        # |
        tenv = RawSet(Signature('tutu', 'toto', 'tata'), Signature('tutu', 'int', 'char')) | RawSet(Signature('blam', 'blim')) |\
               RawSet(Signature('gra', 'gri', 'gru'))
        self.assertIn(Signature('tutu', 'toto', 'tata'), tenv, "Bad | in type_checking.Set")
        self.assertIn(Signature('gra', 'gri', 'gru'), tenv, "Bad | in type_checking.Set")
        # &
        tenv = RawSet(Signature('tutu', 'toto', 'tata'), Signature('tutu', 'int', 'char')) &\
               RawSet(Signature('blam', 'blim'), Signature('tutu', 'toto', 'tata'))
        self.assertIn(Signature('tutu', 'toto', 'tata'), tenv, "Bad & in type_checking.Set")
        self.assertEqual(len(tenv), 1, "Bad & in type_checking.Set")
        # -
        tenv = RawSet(Signature('tutu', 'toto', 'tata'), Signature('tutu', 'int', 'char')) - RawSet(Signature('tutu', 'int', 'char'))
        self.assertIn(Signature('tutu', 'toto', 'tata'), tenv, "Bad - in type_checking.Set")
        self.assertEqual(len(tenv), 1, "Bad - in type_checking.Set")
        # ^
        tenv1 = RawSet(Signature('tutu', 'toto', 'tata'), Signature('tutu', 'int', 'char'), Signature('gra', 'gru'))
        tenv2 = RawSet(Signature('blim', 'blam', 'tata'), Signature('f', 'double', 'char'), Signature('gra', 'gru'), Signature('v', 'd'))
        tenv = tenv1 ^ tenv2
        print(str(tenv1))
        print(str(tenv2))
        print(str(tenv))
        self.assertEqual(len(tenv), 5, "Bad ^ in type_checking.Set")
        self.assertIn(Signature('tutu', 'toto', 'tata'), tenv, "Bad ^ in type_checking.Set")
        self.assertNotIn(Signature('gra', 'gru'), tenv, "Bad ^ in type_checking.Set")

