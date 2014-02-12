import unittest
from pyrser.type_checking.signature import *
from pyrser.type_checking.set import *


class InternalType_Test(unittest.TestCase):

    def test_01_pp(self):
        """
        Test pretty Printing
        """
        var = Signature('var1', 'int')
        f1 = Signature('fun1', 'int', '')
        f2 = Signature('fun2', 'int', 'int')
        f3 = Signature('fun3', 'int', 'int', 'double')
        tenv = Set(None, [var, f1, f2, f3])
        self.assertEqual(str(var), "var var1 : int",
                         "Bad pretty printing of type")
        self.assertEqual(str(f1), "fun fun1 : () -> int",
                         "Bad pretty printing of type")
        self.assertEqual(str(f2), "fun fun2 : (int) -> int",
                         "Bad pretty printing of type")
        self.assertEqual(str(f3), "fun fun3 : (int, double) -> int",
                         "Bad pretty printing of type")
        self.assertEqual(str(tenv), """scope :
    fun fun1 : () -> int
    fun fun2 : (int) -> int
    fun fun3 : (int, double) -> int
    var var1 : int
""", "Bad pretty printing of type")
        t1 = Set('t1', istype=True)
        self.assertEqual(str(t1), "type t1", "Bad pretty printing of type")
        t1.add(Signature('fun1', 'a', 'b'))
        self.assertEqual(str(t1), """type t1 :
    fun t1.fun1 : (b) -> a
""", "Bad pretty printing of type")

    def test_02_setop(self):
        """
        Test Set common operation
        """
        var = Signature('var1', 'int')
        tenv = RawSet(var)
        self.assertIn(Signature('var1', 'int'), tenv,
                      "Bad __contains__ in type_checking.Set")
        tenv.add(Signature('fun1', 'int', 'float', 'char'))
        self.assertIn(Signature('fun1', 'int', 'float', 'char'), tenv,
                      "Bad __contains__ in type_checking.Set")
        ## inplace modification
        # work with any iterable
        tenv |= [Signature('fun2', 'int', 'int')]
        self.assertIn(Signature('fun2', 'int', 'int'), tenv,
                      "Bad __contains__ in type_checking.Set")
        # work with any iterable
        tenv |= {Signature('fun3', 'int', 'int')}
        self.assertIn(Signature('fun3', 'int', 'int'), tenv,
                      "Bad __contains__ in type_checking.Set")
        # retrieves past signature
        v = tenv.get(var.internal_name())
        self.assertEqual(id(v), id(var), "Bad get in type_checking.Set")
        # intersection_update, only with Set
        tenv &= RawSet(Signature('var1', 'int'))
        v = tenv.get(var.internal_name())
        self.assertNotEqual(id(v), id(var), "Bad &= in type_checking.Set")
        # difference_update, only with Set
        tenv |= [Signature('fun2', 'int', 'int'),
                 Signature('fun3', 'char', 'double', 'float')]
        tenv -= RawSet(Signature('var1', 'int'))
        self.assertNotIn(Signature('var1', 'int'), tenv,
                         "Bad -= in type_checking.Set")
        # symmetric_difference_update, only with Set
        tenv ^= RawSet(Signature('var2', 'double'),
                       Signature('fun2', 'int', 'int'),
                       Signature('fun4', 'plop', 'plip', 'ploum'))
        self.assertIn(Signature('fun4', 'plop', 'plip', 'ploum'), tenv,
                      "Bad ^= in type_checking.Set")
        self.assertNotIn(Signature('fun2', 'int', 'int'), tenv,
                         "Bad ^= in type_checking.Set")
        ## binary operation
        # |
        tenv = RawSet(Signature('tutu', 'toto', 'tata'),
                      Signature('tutu', 'int', 'char')) |\
            RawSet(Signature('blam', 'blim')) |\
            RawSet(Signature('gra', 'gri', 'gru'))
        self.assertIn(Signature('tutu', 'toto', 'tata'), tenv,
                      "Bad | in type_checking.Set")
        self.assertIn(Signature('gra', 'gri', 'gru'), tenv,
                      "Bad | in type_checking.Set")
        # &
        tenv = RawSet(Signature('tutu', 'toto', 'tata'),
                      Signature('tutu', 'int', 'char')) &\
            RawSet(Signature('blam', 'blim'),
                   Signature('tutu', 'toto', 'tata'))
        self.assertIn(Signature('tutu', 'toto', 'tata'), tenv,
                      "Bad & in type_checking.Set")
        self.assertEqual(len(tenv), 1, "Bad & in type_checking.Set")
        # -
        tenv = RawSet(Signature('tutu', 'toto', 'tata'),
                      Signature('tutu', 'int', 'char')) -\
            RawSet(Signature('tutu', 'int', 'char'))
        self.assertIn(Signature('tutu', 'toto', 'tata'), tenv,
                      "Bad - in type_checking.Set")
        self.assertEqual(len(tenv), 1, "Bad - in type_checking.Set")
        # ^
        tenv1 = RawSet(Signature('tutu', 'toto', 'tata'),
                       Signature('tutu', 'int', 'char'),
                       Signature('gra', 'gru'))
        tenv2 = RawSet(Signature('blim', 'blam', 'tata'),
                       Signature('f', 'double', 'char'),
                       Signature('gra', 'gru'),
                       Signature('v', 'd'))
        tenv = tenv1 ^ tenv2
        self.assertEqual(len(tenv), 5, "Bad ^ in type_checking.Set")
        self.assertIn(Signature('tutu', 'toto', 'tata'), tenv,
                      "Bad ^ in type_checking.Set")
        self.assertNotIn(Signature('gra', 'gru'), tenv,
                         "Bad ^ in type_checking.Set")

    def test_03_overload(self):
        # test get by symbol name
        tenv = RawSet(Signature('tutu', 'tata'),
                      Signature('plop', 'plip'),
                      Signature('tutu', 'lolo'))
        tenv |= RawSet(Signature('plop', 'gnagna'),
                       Signature('tutu', 'int', 'double'))
        trest = tenv.get_by_symbol_name('tutu')
        self.assertIn(Signature('tutu', 'tata'), trest,
                      "get_by_symbol_name in type_checking.Set")
        self.assertIn(Signature('tutu', 'lolo'), trest,
                      "get_by_symbol_name in type_checking.Set")
        self.assertIn(Signature('tutu', 'int', 'double'), trest,
                      "get_by_symbol_name in type_checking.Set")
        self.assertNotIn(Signature('plop', 'gnagna'), trest,
                         "get_by_symbol_name in type_checking.Set")
        # test get by return type
        tenv = RawSet(Signature('tutu', 'int'),
                      Signature('plop', 'plip'),
                      Signature('tutu', 'int', ''))
        tenv |= RawSet(Signature('plop', 'int'),
                       Signature('tutu', 'int', 'double', 'int'))
        trest = tenv.get_by_return_type('int')
        self.assertIn(Signature('tutu', 'int'), trest,
                      "Bad get_by_return_type in type_checking.Set")
        self.assertIn(Signature('plop', 'int'), trest,
                      "Bad get_by_return_type in type_checking.Set")
        trest = tenv.get_by_return_type('int').get_by_symbol_name('tutu')
        self.assertNotIn(Signature('plop', 'int'), trest,
                         "Bad get_by_return_type in type_checking.Set")
        # test get by params
        f = RawSet(Signature('f', 'void', 'int'),
                   Signature('f', 'int', 'int', 'double', 'char'),
                   Signature('f', 'double', 'int', 'juju'))
        f |= RawSet(Signature('f', 'double', 'char', 'double', 'double'))
        p1 = RawSet(Signature('a', 'int'), Signature('a', 'double'))
        p2 = RawSet(Signature('b', 'int'), Signature('b', 'double'))
        p3 = RawSet(Signature('c', 'int'), Signature('c', 'double'),
                    Signature('c', 'char'))
        (trestf, trestp) = f.get_by_params(p1, p2, p3)
        self.assertIn(Signature('f', 'int', 'int', 'double', 'char'), trestf,
                      "Bad get_by_params in type_checking.Set")
        self.assertEqual(len(trestf), 1,
                         "Bad get_by_params in type_checking.Set")
        self.assertEqual(len(trestp), 3,
                         "Bad get_by_params in type_checking.Set")
        a = trestp.get_by_symbol_name('a')
        self.assertEqual(len(a), 1,
                         "Bad get_by_params in type_checking.Set")
        sa = next(iter(a.values()))
        self.assertEqual(sa.tret, "int",
                         "Bad get_by_params in type_checking.Set")
        b = trestp.get_by_symbol_name('b')
        self.assertEqual(len(b), 1,
                         "Bad get_by_params in type_checking.Set")
        sb = next(iter(b.values()))
        self.assertEqual(sb.tret, "double",
                         "Bad get_by_params in type_checking.Set")
        c = trestp.get_by_symbol_name('c')
        self.assertEqual(len(c), 1,
                         "Bad get_by_params in type_checking.Set")
        sc = next(iter(c.values()))
        self.assertEqual(sc.tret, "char",
                         "Bad get_by_params in type_checking.Set")

    def test_04_symbolpatch(self):
        """
        Test of symbol mangling redefinition.
        For custom language due to multi-inheritance order resolution
        (python MRO), just use follow the good order. Overloads first.
        """
        class MySymbol(Symbol):
            def show_name(sig: Symbol):
                return "cool " + sig.name

            def internal_name(sig: Symbol):
                return "tjrs " + sig.name

        class MySignature(MySymbol, Signature):
            pass
        s = MySignature('funky', 'bla', 'blu')
        self.assertEqual(s.show_name(), 'cool funky',
                         "Bad symbol patching in type_checking")
        self.assertEqual(s.internal_name(), 'tjrs funky',
                         "Bad symbol patching in type_checking")
