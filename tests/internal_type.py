import unittest
from pyrser.type_system import *
from pyrser.passes.to_yml import *
from pyrser.error import *


class InternalType_Test(unittest.TestCase):

    def test_symbol_01_symbolpatch(self):
        """
        Test of symbol mangling redefinition.
        For custom language due to multi-inheritance order resolution
        (python MRO), just use follow the good order. Overloads first.
        """
        class MySymbol(Symbol):
            def show_name(self):
                return "cool " + self.name

            def internal_name(self):
                return "tjrs "

        class MyFun(MySymbol, Fun):
            def internal_name(self):
                return (super().internal_name()
                        + self.name
                        + "."
                        + "_".join(self.tparams)
                        + "." + self.tret
                        )

        s = MyFun('funky', 'bla', ['blu'])
        self.assertEqual(s.show_name(), 'cool funky',
                         "Bad symbol patching in type_system")
        self.assertEqual(s.internal_name(), 'tjrs funky.blu.bla',
                         "Bad symbol patching in type_system")

    def test_scope_01_pp(self):
        """
        Test pretty Printing
        """
        var = Var('var1', 'int')
        f1 = Fun('fun1', 'int', [])
        f2 = Fun('fun2', 'int', ['int'])
        f3 = Fun('fun3', 'int', ['int', 'double'])
        tenv = Scope(sig=[var, f1, f2, f3])
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
        t1 = Type('t1')
        self.assertEqual(str(t1), "type t1", "Bad pretty printing of type")
        t1.add(Fun('fun1', 'a', ['b']))
        self.assertEqual(str(t1), """type t1 :
    fun t1.fun1 : (b) -> a
""", "Bad pretty printing of type")

    def test_scope_02_setop(self):
        """
        Test Scope common operation
        """
        var = Var('var1', 'int')
        tenv = Scope(sig=var)
        self.assertIn(Var('var1', 'int'), tenv,
                      "Bad __contains__ in type_system.Scope")
        tenv.add(Fun('fun1', 'int', ['float', 'char']))
        self.assertIn(Fun('fun1', 'int', ['float', 'char']), tenv,
                      "Bad __contains__ in type_system.Scope")
        ## inplace modification
        # work with any iterable
        tenv |= [Fun('fun2', 'int', ['int'])]
        self.assertIn(Fun('fun2', 'int', ['int']), tenv,
                      "Bad __contains__ in type_system.Scope")
        # work with any iterable
        tenv |= {Fun('fun3', 'int', ['int'])}
        self.assertIn(Fun('fun3', 'int', ['int']), tenv,
                      "Bad __contains__ in type_system.Scope")
        # retrieves past signature
        v = tenv.get(var.internal_name())
        self.assertEqual(id(v), id(var), "Bad get in type_system.Scope")
        # intersection_update, only with Scope
        tenv &= Scope(sig=Var('var1', 'int'))
        v = tenv.get(var.internal_name())
        self.assertNotEqual(id(v), id(var), "Bad &= in type_system.Scope")
        # difference_update, only with Scope
        tenv |= [Fun('fun2', 'int', ['int']),
                 Fun('fun3', 'char', ['double', 'float'])]
        tenv -= Scope(sig=Var('var1', 'int'))
        self.assertNotIn(Var('var1', 'int'), tenv,
                         "Bad -= in type_system.Scope")
        # symmetric_difference_update, only with Scope
        tenv ^= Scope(sig=[Var('var2', 'double'),
                      Fun('fun2', 'int', ['int']),
                      Fun('fun4', 'plop', ['plip', 'ploum'])])
        self.assertIn(Fun('fun4', 'plop', ['plip', 'ploum']), tenv,
                      "Bad ^= in type_system.Scope")
        self.assertNotIn(Fun('fun2', 'int', ['int']), tenv,
                         "Bad ^= in type_system.Scope")
        ## binary operation
        # |
        tenv = Scope(sig=[Fun('tutu', 'toto', ['tata']),
                     Fun('tutu', 'int', ['char'])]) |\
            Scope(sig=Fun('blam', 'blim', [])) |\
            Scope(sig=Fun('gra', 'gri', ['gru']))
        self.assertIn(Fun('tutu', 'toto', ['tata']), tenv,
                      "Bad | in type_system.Scope")
        self.assertIn(Fun('gra', 'gri', ['gru']), tenv,
                      "Bad | in type_system.Scope")
        # &
        tenv = Scope(sig=[Fun('tutu', 'toto', ['tata']),
                     Fun('tutu', 'int', ['char'])]) &\
            Scope(sig=[Fun('blam', 'blim', []),
                  Fun('tutu', 'toto', ['tata'])])
        self.assertIn(Fun('tutu', 'toto', ['tata']), tenv,
                      "Bad & in type_system.Scope")
        self.assertEqual(len(tenv), 1, "Bad & in type_system.Scope")
        # -
        tenv = Scope(sig=[Fun('tutu', 'toto', ['tata']),
                     Fun('tutu', 'int', ['char'])]) -\
            Scope(sig=Fun('tutu', 'int', ['char']))
        self.assertIn(Fun('tutu', 'toto', ['tata']), tenv,
                      "Bad - in type_system.Scope")
        self.assertEqual(len(tenv), 1, "Bad - in type_system.Scope")
        # ^
        tenv1 = Scope(sig=[Fun('tutu', 'toto', ['tata']),
                      Fun('tutu', 'int', ['char']),
                      Fun('gra', 'gru', [])])
        tenv2 = Scope(sig=[Fun('blim', 'blam', ['tata']),
                      Fun('f', 'double', ['char']),
                      Fun('gra', 'gru', []),
                      Fun('v', 'd', [])])
        tenv = tenv1 ^ tenv2
        self.assertEqual(len(tenv), 5, "Bad ^ in type_system.Scope")
        self.assertIn(Fun('tutu', 'toto', ['tata']), tenv,
                      "Bad ^ in type_system.Scope")
        self.assertNotIn(Fun('gra', 'gru', []), tenv,
                         "Bad ^ in type_system.Scope")

    def test_scope_03_overload(self):
        # test get by symbol name
        tenv = Scope(sig=[Fun('tutu', 'tata', []),
                     Fun('plop', 'plip', []),
                     Fun('tutu', 'lolo', [])])
        tenv |= Scope(sig=[Fun('plop', 'gnagna'),
                      Fun('tutu', 'int', ['double'])])
        trest = tenv.get_by_symbol_name('tutu')
        self.assertIn(Fun('tutu', 'tata'), trest,
                      "get_by_symbol_name in type_system.Scope")
        self.assertIn(Fun('tutu', 'lolo'), trest,
                      "get_by_symbol_name in type_system.Scope")
        self.assertIn(Fun('tutu', 'int', ['double']), trest,
                      "get_by_symbol_name in type_system.Scope")
        self.assertNotIn(Fun('plop', 'gnagna'), trest,
                         "get_by_symbol_name in type_system.Scope")
        # test get by return type
        tenv = Scope(sig=[Fun('tutu', 'int'),
                     Fun('plop', 'plip'),
                     Fun('tutu', 'int', [])])
        tenv |= Scope(sig=[Fun('plop', 'int'),
                      Fun('tutu', 'int', ['double', 'int'])])
        trest = tenv.get_by_return_type('int')
        self.assertIn(Fun('tutu', 'int'), trest,
                      "Bad get_by_return_type in type_system.Scope")
        self.assertIn(Fun('plop', 'int'), trest,
                      "Bad get_by_return_type in type_system.Scope")
        trest = tenv.get_by_return_type('int').get_by_symbol_name('tutu')
        self.assertNotIn(Fun('plop', 'int'), trest,
                         "Bad get_by_return_type in type_system.Scope")
        # test get by params
        f = Scope(sig=[Fun('f', 'void', ['int']),
                  Fun('f', 'int', ['int', 'double', 'char']),
                  Fun('f', 'double', ['int', 'juju'])])
        f |= Scope(sig=Fun('f', 'double', ['char', 'double', 'double']))
        p1 = Scope(sig=[Fun('a', 'int'), Fun('a', 'double')])
        p2 = Scope(sig=[Fun('b', 'int'), Fun('b', 'double')])
        p3 = Scope(sig=[Fun('c', 'int'), Fun('c', 'double'),
                   Fun('c', 'char')])
        (trestf, trestp) = f.get_by_params([p1, p2, p3])
        self.assertIn(Fun('f', 'int', ['int', 'double', 'char']), trestf,
                      "Bad get_by_params in type_system.Scope")
        self.assertEqual(len(trestf), 1,
                         "Bad get_by_params in type_system.Scope")
        self.assertEqual(len(trestp), 1,
                         "Bad get_by_params in type_system.Scope")
        self.assertEqual(len(trestp[0]), 3,
                         "Bad get_by_params in type_system.Scope")
        self.assertEqual(len(trestp[0][0]), 1,
                         "Bad get_by_params in type_system.Scope")
        self.assertEqual(len(trestp[0][1]), 1,
                         "Bad get_by_params in type_system.Scope")
        self.assertEqual(len(trestp[0][2]), 1,
                         "Bad get_by_params in type_system.Scope")
        a = trestp[0][0].get_by_symbol_name('a')
        self.assertEqual(len(a), 1,
                         "Bad get_by_params in type_system.Scope")
        sa = next(iter(a.values()))
        self.assertEqual(sa.tret, "int",
                         "Bad get_by_params in type_system.Scope")
        b = trestp[0][1].get_by_symbol_name('b')
        self.assertEqual(len(b), 1,
                         "Bad get_by_params in type_system.Scope")
        sb = next(iter(b.values()))
        self.assertEqual(sb.tret, "double",
                         "Bad get_by_params in type_system.Scope")
        c = trestp[0][2].get_by_symbol_name('c')
        self.assertEqual(len(c), 1,
                         "Bad get_by_params in type_system.Scope")
        sc = next(iter(c.values()))
        self.assertEqual(sc.tret, "char",
                         "Bad get_by_params in type_system.Scope")

    def test_scope_04_links_embedded(self):
        # if scope is not a namespace, don't auto-prefix signature
        s1 = Scope("coucou", is_namespace=True)
        s1.add(Fun("f1", "t1"))
        t = Type("t1")
        s1.add(t)
        f = Fun("f2", "t2")
        s1.add(f)
        self.assertEqual(s1.state, StateScope.FREE, "Bad state of Scope")
        self.assertIn(f, s1, "Can't found function in Scope")
        # TODO: fix namespace to a better way
        #self.assertIn(t, s1, "Can't found type in Scope")
        # if scope is a namespace, auto-prefix signature
        s1 = Scope("coucou", is_namespace=True)
        s1.add(Fun("f1", "t1"))
        s1.add(Type("t1"))
        f = Fun("f2", "t2")
        s1.add(f)
        self.assertEqual(f.internal_name(), "coucou_f2_t2", "Internal name of function without prefix")
        self.assertEqual(s1.state, StateScope.FREE, "Bad state of Scope")
        self.assertIn(f, s1, "Can't found function with prefix")
        self.assertNotIn(Fun("f2", "t2"), s1, "Shouldn't found function without prefix")
        # links between 2 scope
        s1 = Scope(sig=[Var('a', 't1'), Fun('f', 't2'), Type("t4")])
        s2 = Scope("namespace2", sig=[Var('a', 't3'), Fun('f', 't4')])
        s2.set_parent(s1)
        self.assertEqual(s2.state, StateScope.LINKED, "Bad state of Scope")
        f = Fun('f2', 't5')
        s1.add(f)
        self.assertNotIn(f, s2, "Bad query __contains__ for StateScope.LINKED")
        # linked scope forward type query
        self.assertIn(Type("t4"), s2, "Bad query __contains__ for StateScope.LINKED")
        # embedded scopes
        s1 = Scope(sig=[Var('a', 't1'), Fun('f', 't2')])
        s2 = Scope("n2", sig=[Var('a', 't3'), Fun('f', 't4')])
        s1.add(s2)
        self.assertEqual(s2.state, StateScope.EMBEDDED, "Bad state of Scope")
        f = Fun('f2', 't5')
        s1.add(f)
        # embedded scope forward signature query
        self.assertIn(f, s2, "Bad query __contains__ for StateScope.EMBEDDED")

    def test_scope_05_save_restore(self):
        import pickle
        s1 = Scope("namespace1", sig=[Var('a', 't1'), Fun('f', 't2')])
        # TODO: works on Scope serialization !!!
        #print(pickle.dumps(s1))

    def test_val_01_pp(self):
        val1 = Val(12, "int")
        val2 = Val(12, "byte")
        val3 = Val(12, "char")
        val4 = Val(12, "short")
        val5 = Val(12, "short")
        val6 = Val('a', "char")
        val7 = Val('"toto"', "string")
        self.assertEqual(str(val1), "val $1 (12) : int",
                         "Bad pretty-print in type_system.Val")
        self.assertEqual(str(val2), "val $2 (12) : byte",
                         "Bad pretty-print in type_system.Val")
        self.assertEqual(str(val3), "val $3 (12) : char",
                         "Bad pretty-print in type_system.Val")
        self.assertEqual(str(val4), "val $4 (12) : short",
                         "Bad pretty-print in type_system.Val")
        self.assertEqual(str(val5), "val $4 (12) : short",
                         "Bad pretty-print in type_system.Val")
        self.assertEqual(str(val6), "val $5 (a) : char",
                         "Bad pretty-print in type_system.Val")
        self.assertEqual(str(val7), 'val $6 ("toto") : string',
                         "Bad pretty-print in type_system.Val")

    def test_poly_01_var(self):
        # ?1 means type placeholders for polymorphisme
        var = Scope(sig=Var('var1', '?1'))
        self.assertTrue(
            var.getsig_by_symbol_name("var1").is_polymorphic,
            "Bad Var interface"
        )
        tenv = Scope(sig=Fun('fun1', 'int', ['char']))
        (trestf, trestp) = tenv.get_by_params([var])
        self.assertIn(Fun('fun1', 'int', ['char']), trestf,
                      "Bad polymorphic in type_system.Scope")
        self.assertIn(Var('var1', '?1'), trestp[0][0],
                      "Bad polymorphic in type_system.Scope")
        var = Scope(sig=Var('var1', 'int'))
        tenv = Scope(sig=Fun('fun1', 'int', ['?1']))
        self.assertTrue(
            tenv.getsig_by_symbol_name("fun1").is_polymorphic,
            "Bad Fun interface"
        )
        (trestf, trestp) = tenv.get_by_params([var])
        self.assertIn(Fun('fun1', 'int', ['?1']), trestf,
                      "Bad polymorphic in type_system.Scope")
        self.assertIn(Var('var1', 'int'), trestp[0][0],
                      "Bad polymorphic in type_system.Scope")

    def test_variadic_01(self):
        tenv = Scope(sig=[Fun('printf', 'void', ['const * char'],
                     variadic=True),
                     Fun('printf', 'void', ['int'])])
        sel = tenv.get_by_symbol_name('printf')
        var = Scope(sig=Var('v', 'const * char'))
        val = Scope(sig=Val('666', 'int'))
        (trestf, trestp) = sel.get_by_params([var, val])
        self.assertEqual(len(trestf), len(trestp), "Bad candidates")
        self.assertEqual(
            int(trestp[0][1].get(val.pop()[0]).value),
            666,
            "Bad candidates"
        )

    def test_type_name_01_pp(self):
        tn = TypeName("* const int")
        var = Var('var1', tn)
        self.assertEqual(str(var), "var var1 : * const int",
                         "Bad TypeName in type_system.Var")

    def test_tuple_01_pp(self):
        tp = Tuple([Fun(None, 'X'), Var(None, 'U'), Var(None, 'T')])
        self.assertEqual(str(tp), "tuple(fun : () -> X, var : U, var : T)",
                         "Bad pretty-printing in type_system.Tuple")

    def test_eval_ctx_01(self):
        ectx = EvalCtx(Fun("f", "int", ["double"]))
        self.assertEqual(str(ectx), """evalctx :
    fun f : (double) -> int
    resolution :
        'double': Unresolved
        'int': Unresolved
""",
                         "Bad TypeName in type_system.EvalCtx")
        typ = Type("T1")
        typ.add(Fun("f", "int", ["int"]))
        tenv = Scope("test", sig=typ)
        tenv.add(EvalCtx(Fun("f", "T1")))
        fs = tenv.get_by_symbol_name("f")
        self.assertEqual(
            id(typ),
            id(
                list(
                    tenv.get_by_symbol_name("f").values()
                )[0].resolution['T1']()
            ),
            "Bad resolution in type_system.EvalCtx"
        )

    def test_translator_01(self):
        with self.assertRaises(TypeError):
            t = Translator(1, 2)
        with self.assertRaises(TypeError):
            t = Translator(Fun('pouet', 't2'), 2)
        with self.assertRaises(TypeError):
            t = Translator(
                Fun('pouet', 't2'),
                Notification(Severity.INFO, "pouet", None)
            )
        f = Fun('newT2', 'T2', ['T1'])
        trans = Translator(
            f,
            Notification(
                Severity.INFO,
                "Convert T1 into T2",
                LocationInfo.from_here()
            )
        )
        lines = str(trans.to_fmt()).split('\n')
        self.assertEqual(lines[0], "T1 to T2 = fun newT2 : (T1) -> T2")
        m = MapTargetTranslate()
        with self.assertRaises(TypeError):
            m[1] = 2
        with self.assertRaises(KeyError):
            m[1] = trans
        with self.assertRaises(KeyError):
            m["Z"] = trans
        m["T2"] = trans
        m["T3"] = Translator(
            Fun("init", 'T3', ['T1']),
            Notification(
                Severity.INFO,
                "Implicit T1 to T3",
                LocationInfo.from_here()
            )
        )
        self.assertEqual(
            repr(m["T3"]),
            "T1 to T3 = fun init : (T1) -> T3\ninfo : Implicit T1 to T3\n",
            "Bad Translator pretty-printing"
        )
        mall = MapSourceTranslate()
        mall["T1"] = m
        mall.addTranslator(
            Translator(
                Fun("__builtin_cast", "int", ["char"]),
                Notification(
                    Severity.INFO,
                    "implicit convertion",
                    LocationInfo.from_here()
                )
            )
        )
        self.assertEqual(
            repr(mall["char"]["int"]),
            ("char to int = fun __builtin_cast : (char) -> int\n"
             + "info : implicit convertion\n"),
            "Bad Translator pretty-printing"
        )
        self.assertTrue(
            ("char", "int") in mall,
            "Bad MapSourceTranslate interface"
        )
        self.assertTrue(
            ("T1", "T3") in mall,
            "Bad MapSourceTranslate interface"
        )
        res = ("T1", "T3") in mall
        self.assertTrue(res, "Bad MapSourceTranslate interface")
        mall2 = MapSourceTranslate()
        mall2.addTranslator(
            Translator(
                Fun("to_string", "string", ["int"]),
                Notification(
                    Severity.INFO,
                    "cast to string",
                    LocationInfo.from_here()
                )
            )
        )
        mall2.set_parent(mall)
        self.assertTrue(
            ("T1", "T3") in mall2,
            "Bad MapSourceTranslate interface"
        )
        mall.addTranslator(
            Translator(
                Fun("to_int", "int", ["string"]),
                Notification(
                    Severity.INFO,
                    "cast to int",
                    LocationInfo.from_here()
                )
            )
        )
        self.assertTrue(
            ("string", "int") in mall2,
            "Bad MapSourceTranslate interface"
        )
        mall2.addTranslator(
            Translator(
                Fun("to_float", "float", ["string"]),
                Notification(
                    Severity.INFO,
                    "cast to float",
                    LocationInfo.from_here()
                )
            ),
            as_global=True
        )
        self.assertTrue(
            ("string", "float") in mall,
            "Bad MapSourceTranslate interface"
        )

    def test_translator_02(self):
        n = Notification(
            Severity.INFO,
            "implicit conversion",
            LocationInfo.from_here()
        )
        f = Fun("to_int", "int", ["string"])
        s = Scope(sig=[f])
        s.mapTypeTranslate.addTranslator(Translator(f, n))
        f = Fun("to_float", "float", ["string"])
        s |= Scope(sig=[f])
        s.mapTypeTranslate.addTranslator(Translator(f, n))
        f = Fun("char2int", "int", ["char"])
        s |= Scope(sig=[f])
        s.mapTypeTranslate.addTranslator(Translator(f, n))
        v1 = Var("a", "string")
        v2 = Var("a", "float")
        isgood = Fun("isgood", "bool", ["int"])
        s |= Scope(sig=[isgood, v1, v2])
        v = s.get_by_symbol_name('a')
        (res, sig, trans) = v.findTranslationTo(isgood.tparams[0])
        self.assertTrue(res, "Can't found the good translator")
        self.assertEqual(sig.tret, "string", "Bad type for var a")
        s.add(Var("b", "string"))
        s.add(Var("b", "X"))
        s.add(Fun("f", "int", ["int"]))
        s.add(Fun("f", "float", ["char"]))
        f = s.get_by_symbol_name("f")
        v = s.get_by_symbol_name("b")
        (fns, params) = f.get_by_params([v])
        self.assertTrue(
            params[0][0].first()._translate_to is not None,
            "Can't find translator"
        )
        self.assertEqual(
            params[0][0].first()._translate_to.target,
            "int",
            "Can't reach the return type"
        )
