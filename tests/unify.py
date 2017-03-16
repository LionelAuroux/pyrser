import unittest
from weakref import ref
from pyrser import meta
from tests.grammar.tl4t import *

### Type Expr component

class TypeExprComponent(list):
    contains = None
    minarity = None
    def __init__(self, *deflist):
        if self.minarity is not None and len(deflist) < self.minarity:
            raise TypeError("%s take minimum %d parameters" % (type(self).__name__, self.minarity))
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

    def __repr__(self) -> str:
        return str(self)

class Define:
    def __init__(self, name: str, type_def: TypeExprComponent):
        self.name = name
        self.type_def = type_def

    def __len__(self) -> int:
        return len(self.type_def)

    def __getitem__(self, idx) -> TypeExprComponent:
        return self.type_def[idx]

    def __str__(self) -> str:
        return "%s: %s" % (self.name, self.type_def)

    def __repr__(self) -> str:
        return str(self)

class AnonDefine(Define):
    """
    Implement the TypeVar: ?0, ?1, ?2, ...
    """
    count = 0
    def __init__(self, type_def: TypeExprComponent = None):
        """
        TODO: not really the final version
        """
        Define.__init__(self, '?%d' % AnonDefine.count, None)
        AnonDefine.count += 1

class Overload(TypeExprComponent):
    contains = {'Fun', 'T', 'N'}
    minarity = 1

    def __str__(self) -> str:
        return "\n& ".join(self.reprlist)

class Fun(TypeExprComponent):
    contains = {'Union', 'Tuple', 'T', 'N'}
    minarity = 2

    def __str__(self) -> str:
        return " -> ".join(reversed(self.reprlist))

class Union(TypeExprComponent):
    contains = {'Union', 'T', 'N'}
    minarity = 2

    def __str__(self) -> str:
        return " | ".join(self.reprlist)

class Tuple(TypeExprComponent):
    contains = {'Fun', 'Union', 'Tuple', 'T', 'N'}
    minarity = 2

    def __str__(self) -> str:
        return ", ".join(self.reprlist)

class N(TypeExprComponent):
    """N for Namespaces"""
    contains = {'T'}
    minarity = 2

    def __str__(self) -> str:
        return ".".join(self.reprlist)

class T:
    """T for Type"""
    def __init__(self, name: str, parametric: Tuple or 'T'=None, attributes=None):
        self.name = name
        if parametric is not None and type(parametric) not in {Tuple, T}:
            raise TypeError("T parametric must be a Tuple")
        self.parametric = parametric
        self.attributes = attributes

    def __eq__(self, oth) -> bool:
        """
        Use by all __contains__ call when we do some 'in' test
        """
        # TODO: self and oth for comparaison with TypeVar, attributes and parametric
        return self.name == oth

    def __str__(self) -> str:
        r = self.name
        if self.parametric is not None:
            r += '<' + str(self.parametric) + '>'
        return r

    def __repr__(self) -> str:
        return str(self)

########### TODO voir pour Binding
from collections import ChainMap

class Bind:
    def __init__(self, cnt):
        self.cnt = cnt
        self.src = None
        self.dst = None
        self.flag = {'to_visit'}

    def __str__(self) -> str:
        r = "\nid: %d" % id(self)
        r += "\ndef: %s" % str(self.cnt.defs)
        if self.src is not None:
            r += "\nsrc: %s" % str(self.src)
        if self.dst is not None:
            r += "\ndst: %s" % str(self.dst)
        return r
    
    def __repr__(self) -> str:
        return str(self)

    @property
    def resolvable(self) -> bool:
        return self.src is not None and self.dst is not None

    def unify(self):
        print("Unify %s" % str(self.adef))

class Constraints:
    def __init__(self, initial_defs: [Define]=None):
        # store definitions
        self.defs = []
        # map name -> idx in defs
        self.name2id = ChainMap()
        self.add_defines(initial_defs)
        # ...
        self.top_down = []
        self.bottom_up = []
        self.mapbind = {}

    def add_defines(self, defs: [Define]):
        if defs is not None and type(defs) is not list:
            raise TypeError("Constraints took a list of Define.")
        for idx, it in zip(range(len(defs)), defs):
            if type(it) is not Define:
                raise TypeError("Param %d is not a define" % idx)
        nodef = len(self.defs)
        ndef = len(defs)
        self.defs += defs
        for it, idx in zip(defs, range(ndef)):
            self.name2id[it.name] = nodef + idx

    def push_context(self):
        self.name2id = self.name2id.new_child()

    def pop_context(self):
        for idx in sorted(self.name2id.maps[0].values(), reverse=True):
            self.defs.pop(idx)
        self.name2id = self.name2id.parents

    def __str__(self) -> str:
        r = ""
        r += "\ndefs:\n%s" % str(self.defs)
        r += "\nname2id: %s" % repr(self.name2id)
        if len(self.mapbind) > 0:
            r += "\nmapbind: %s" % repr(self.mapbind)
        return r

    def get_def(self, name: str) -> Define:
        return self.defs[self.name2id[name]]

    def get_bind_id(self, src) -> int:
        bid = id(src)
        if bid not in self.mapbind:
            self.mapbind[bid] = src
        return bid

    def add_BU_cnt(self, src):
        id_src = self.get_bind_id(src)
        self.bottom_up.append(id_src)

    def add_TD_cnt(self, src):
        id_src = self.get_bind_id(src)
        self.top_down.append(id_src)

    def resolve(self):
        while True:
            done_something = False
            while True:
                if len(self.bottom_up) == 0:
                    break
                it = self.bottom_up.pop()
                b = self.mapbind[it]
                print("BU %d" % it)
                if 'to_resolve' in b.flag and b.resolvable:
                    b.unify()
                    done_something = True
            while True:
                if len(self.top_down) == 0:
                    break
                it = self.top_down.pop()
                b = self.mapbind[it]
                print("TD %d" % it)
                if 'to_visit' in b.flag:
                    print("visit %d" % it)
                    if b.src is not None:
                        p = b.src
                        print("add %d" % id(p))
                        self.add_TD_cnt(p)
                        self.add_BU_cnt(p)
                    if b.dst is not None:
                        for p in b.dst:
                            print("add %d" % id(p))
                            self.add_TD_cnt(p)
                            self.add_BU_cnt(p)
                    b.flag = {'to_resolve'}
                    done_something = True
            if not done_something:
                break

#####################

## for each language you must visit your tree and populate the Constraints
## Create a Bind object and add it in the contraint object
## Add a TD if need
@meta.add_method(BlockStmt)
def populate(self, cnt: Constraints):
    print("Add %s constraint" % type(self).__name__)
    cnt.push_context()
    for it in self.body:
        it.populate(cnt)
    cnt.pop_context()

@meta.add_method(DeclVar)
def populate(self, cnt: Constraints):
    print("Add %s constraint" % type(self).__name__)
    d = Define(self.name, T(self.t))
    cnt.add_defines([d])
    self.expr.populate(cnt)
    b = Bind(cnt)
    b.src = d
    b.dst = self.expr
    cnt.add_TD_cnt(b)
    

@meta.add_method(DeclFun)
def populate(self, cnt: Constraints):
    print("Add %s constraint" % type(self).__name__)
    # TODO: namespace/parametric/variadic...
    d = Define(self.name, Fun(T(self.t, *self.p)))
    cnt.add_defines([d])
    for it in self.block:
        it.populate(cnt)
    b = Bind(cnt)
    b.src = d
    b.dst = self.block
    cnt.add_TD_cnt(b)

@meta.add_method(ExprStmt)
def populate(self, cnt: Constraints):
    print("Add %s constraint" % type(self).__name__)
    self.expr.populate(cnt)

@meta.add_method(Expr)
def populate(self, cnt: Constraints):
    print("Add %s constraint" % type(self).__name__)
    self.call_expr.populate(cnt)
    for it in self.p:
        it.populate(cnt)
    b = Bind(cnt)
    # TODO: Found the definition of expr
    b.src = self.call_expr
    b.dst = self.p
    cnt.add_TD_cnt(b)

@meta.add_method(Id)
def populate(self, cnt: Constraints):
    print("Add %s constraint" % type(self).__name__)
    print(self.value)
    b = Bind(cnt)
    # TODO: Found the definition of self.value
    cnt.add_BU_cnt(b)

@meta.add_method(Operator)
def populate(self, cnt: Constraints):
    print("Add %s constraint" % type(self).__name__)
    print(self.value)
    b = Bind(cnt)
    # TODO: Found the definition of operator

@meta.add_method(Literal)
def populate(self, cnt: Constraints):
    print("Add %s constraint" % type(self).__name__)
    print(self.value)
    b = Bind(cnt)
    # TODO: Found the type of the literal
    cnt.add_BU_cnt(b)

class Unifying_Test(unittest.TestCase):

    def test_000(self):
        """Pretty Print Test"""
        d = Overload(T("t1"), T("t2"))
        self.assertEqual(str(d), "t1\n& t2")
        d = Fun(T("t1"), T("t2"))
        self.assertEqual(str(d), "t2 -> t1")
        d = Fun(T("t1"), T("t2"))
        self.assertEqual(str(d), "t2 -> t1")
        d = Union(T("t1"), T("t2"))
        self.assertEqual(str(d), "t1 | t2")
        d = Tuple(T("t1"), T("t2"))
        self.assertEqual(str(d), "t1, t2")
        d = Fun(T('t3'), Tuple(T("t1"), T("t2")))
        self.assertEqual(str(d), "(t1, t2) -> t3")
        def1 = Define('v1', T('t1'))
        self.assertEqual(str(def1), "v1: t1")
        def1 = Define('v1', N(T('m1'), T('m2'), T('t1')))
        self.assertEqual(str(def1), "v1: m1.m2.t1")
        def1 = Define('v1', N(T('m1', T('T')), T('t1')))
        self.assertEqual(str(def1), "v1: m1<T>.t1")

    def test_001(self):
        """Composition Test"""
        d = Overload(Fun(T("t1"), Tuple(T("t2"), T("t3"))),
            Fun(T("t4"), Tuple(T("t2"), T("t4")))
            )
        self.assertEqual(str(d), "(t2, t3) -> t1\n& (t2, t4) -> t4")
        with self.assertRaises(TypeError):
            d = Overload(Overload(T("t2"), T("t3")))
        with self.assertRaises(TypeError):
            d = Overload(Union(T("t2"), T("t3")))
        with self.assertRaises(TypeError):
            d = Overload(Tuple(T("t2"), T("t3")))
        with self.assertRaises(TypeError):
            d = Fun(Overload(T("t2"), T("t3")))
        with self.assertRaises(TypeError):
            d = Fun(Fun(T("t2"), T("t3")))
        with self.assertRaises(TypeError):
            d = Union(Overload(T("t2"), T("t3")))
        with self.assertRaises(TypeError):
            d = Union(Fun(T("t2"), T("t3")))
        with self.assertRaises(TypeError):
            d = Tuple(Overload(T("t2"), T("t3")))

    def test_002(self):
        """Constraints class tests"""
        basic_a =Define("A", None)
        cnt = Constraints([basic_a, Define("B", None), Define("C", None)])
        self.assertEqual(cnt.get_def("A").name, "A", "Can't find a basic define")
        self.assertEqual(cnt.get_def("B").name, "B", "Can't find a basic define")
        cnt.push_context()
        d = Define("A", Fun(T("t1"), T("t2")))
        cnt.add_defines([d])
        self.assertEqual(cnt.get_def("A"), d, "Can't find a basic define")
        cnt.pop_context()
        self.assertEqual(cnt.get_def("A"), basic_a, "Can't find a basic define")
        cnt.push_context()
        d1 = Define("A", Fun(T("t3"), T("t4")))
        d2 = Define("B", Fun(T("t5"), T("t6")))
        d3 = Define("Z", Fun(T("t7"), T("t8")))
        d4 = Define("X", Fun(T("t9"), T("t10")))
        cnt.add_defines([d1, d2, d3, d4])
        self.assertEqual(cnt.get_def("X"), d4, "Can't find a basic define")
        self.assertEqual(cnt.get_def("A"), d1, "Can't find a basic define")
        self.assertEqual(cnt.get_def("Z"), d3, "Can't find a basic define")
        self.assertEqual(cnt.get_def("B"), d2, "Can't find a basic define")
        cnt.pop_context()
        self.assertEqual(cnt.get_def("A"), basic_a, "Can't find a basic define")

    def test_003(self):
        """Basic unification.
        We assume the Binding (link item to type definition is done.
        """
        # just unification for a Fun
        overloads = Overload(
                Fun(T("t1"), T("t2"), T("t3")),
                Fun(T("t4"), T("t2"), T("t5"))
            )
        def_f = Define("f", overloads)
        print(def_f)
        # v = f(a, b)
        def_a = Define("a", Overload(T("t1"), T("t2")))
        def_b = Define("b", Overload(T("t3"), T("t0")))
        def_v = Define("v", Overload(T("t1"), T("t4")))

        ####
        from itertools import product

        fun_args = [def_v, def_a, def_b]
        # make the product of all possible signature
        selected_sig = []
        arg_pos = [range(len(arg)) for arg in fun_args]
        for types_tuple in product(*arg_pos):
            print(types_tuple)
            # make a proposition
            possible_sig = [arg[idx] for arg, idx in zip(fun_args, types_tuple)]
            print(possible_sig)
            # if is good, take it
            if possible_sig in def_f:
                selected_sig.append(possible_sig)
        print(selected_sig)

        # unification and grammar
        # f: t2 -> t1
        def1 = Define("f", Fun(T("t1"), T("t2")))
        # a: t2
        def2 = Define("a", T("t2"))
        # v: t1
        def3 = Define("v", T("t1"))
        # Test it with a little grammar
        test = TL4T()
        res = test.parse("""
            v = f(a);
        """)
        txt = res.to_tl4t()
        print(txt)
        cnt = Constraints([def1, def2, def3])
        print(cnt)
        res.populate(cnt)
        print(cnt)
        cnt.resolve()
