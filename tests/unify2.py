import unittest
from pyrser.type_system.type_expr2 import *

#########################

class Unifying_Test(unittest.TestCase):

    def test_000(self):
        """Pretty Print Test"""
        d = Overload(T("t1"), T("t2"), T("t3"))
        self.assertEqual(str(d), "t1\n^ t2\n^ t3")
        d = Fun(T("t1"), T("t2"), T("t3"))
        self.assertEqual(str(d), "t3 -> t2 -> t1")
        d = Fun(T("t1"), T("t2"))
        self.assertEqual(str(d), "t2 -> t1")
        d = Union(T("t1"), T("t2"))
        self.assertEqual(str(d), "t1 | t2")
        d = Tuple(T("t1"), T("t2"))
        self.assertEqual(str(d), "t1 * t2")
        d = Fun(T('t3'), Tuple(T("t1"), T("t2")))
        self.assertEqual(str(d), "(t1 * t2) -> t3")
        s = Scope()
        def1 = Define('v1', T('t1'), s)
        self.assertEqual(str(def1), "v1: t1")
        def1 = Define('v1', N(T('m1'), T('m2'), T('t1')), s)
        self.assertEqual(str(def1), "v1: m1.m2.t1")
        def1 = Define('v1', N(T('m1', T('T')), T('t1')), s)
        self.assertEqual(str(def1), "v1: m1<T>.t1")

    def test_001(self):
        """Composition Test"""
        d = Overload(Fun(T("t1"), Tuple(T("t2"), T("t3"))),
            Fun(T("t4"), Tuple(T("t2"), T("t4")))
            )
        self.assertEqual(str(d), "(t2 * t3) -> t1\n^ (t2 * t4) -> t4")
        with self.assertRaises(TypeError):
            d = Overload(Overload(T("t2"), T("t3")))
        with self.assertRaises(TypeError):
            d = Overload(Union(T("t2"), T("t3")))
        with self.assertRaises(TypeError):
            d = Overload(Tuple(T("t2"), T("t3")))
        with self.assertRaises(TypeError):
            d = Fun(Overload(T("t2"), T("t3")))
        with self.assertRaises(TypeError):
            d = Union(Overload(T("t2"), T("t3")))
        with self.assertRaises(TypeError):
            d = Union(Fun(T("t2"), T("t3")))
        with self.assertRaises(TypeError):
            d = Tuple(Overload(T("t2"), T("t3")))

    def test_002(self):
        """Constraints class tests"""
        # 2 term doesn't match
        a = Term()
        b = Term()
        s = Scope()
        r = s.unify(a, b)
        self.assertFalse(r, "failed to mismatch to different term")
        # unknowName always match a term and capture it
        a = Term()
        t = UnknownName()
        s = Scope()
        r = s.unify(a, t)
        self.assertTrue(r, "failed to unify a simple term")
        self.assertIs(t.link(), a, "failed to refer the same term")
        # definition are inside a Scope
        s = Scope()
        a = Define('a', Term(), s)
        b = Define('b', Term(), s)
        r = s.unify(s.get('a'), s.get('b'))
        self.assertFalse(r, "failed to detect a simple mismatch")
        # expression are just related to defined term
        s = Scope()
        t = Define('t', Term(), s)
        ea = Expr('t', s)
        eb = Expr('t', s)
        r = s.unify(ea, eb)
        self.assertTrue(r, "failed to detect a simple match between to expression of the same term")
        # literal expression are assoc with a term (builtin type)
        s = Scope()
        t1 = Define('int', Term(), s)
        e = ExprLiteral('12', 'int', s)
        self.assertIs(e.find(), t1.type_def, "failed to find the type of a literal")
        # unknowName are related to captured Term thru expression matching
        s = Scope()
        t1 = Define('t1', Term(), s)
        t2 = Define('t2', UnknownName(), s)
        ea = Expr('t1', s)
        eb = Expr('t2', s)
        r = s.unify(ea, eb)
        self.assertTrue(r, "failed to detect a match with a TypeVar")
        self.assertIs(t2.type_def.link(), t1.type_def, "failed to detect a simple match")
        # calling expression
        l = Log()
        s = Scope()
        t1 = Define('t1', Term(), s)
        t2 = Define('t2', Term(), s)
        tf = Define('f', Fun(t2.type_def, t1.type_def), s)
        a = Expr('t1', s)
        f = ExprFun('f', [a], s)
        print("=" * 20)
        r = s.unify(f, None)
        s.log_it(l)
        print(str(l))
        self.assertTrue(r, "failed to detect a match of a function")
