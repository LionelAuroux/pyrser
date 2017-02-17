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

    def __str__(self) -> str:
        return "%s: %s" % (self.name, self.type_def)

    def __repr__(self) -> str:
        return str(self)

class AnonDefine(Define):
    count = 0
    def __init__(self, type_def: TypeExprComponent):
        AnonDefine.count += 1
        Define.__init__(self, '?%d' % AnonDefine.count, type_def)

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

    def __str__(self) -> str:
        r = self.name
        if self.parametric is not None:
            r += '<' + str(self.parametric) + '>'
        return r

    def __repr__(self) -> str:
        return str(self)

########### TODO voir pour Binding

class Bind:
    def __init__(self, adef: Define):
        self.adef = adef
        self.src = None
        self.dst = None
        self.flag = {'to_visit'}

    def __str__(self) -> str:
        r = "\nid: %d" % id(self)
        r += "\nadef: %s" % str(self.adef)
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
    def __init__(self, defs: [Define]):
        if type(defs) is not list:
            raise TypeError("Constraints took a list of Define.")
        for idx, it in zip(range(len(defs)), defs):
            if type(it) is not Define:
                raise TypeError("Param %d is not a define" % idx)
        self.defs = defs
        self.name2def = {}
        for it in defs:
            self.name2def[it.name] = ref(it)
        self.top_down = []
        self.bottom_up = []
        self.mapbind = {}

    def __str__(self) -> str:
        r = ""
        r += "\ndefs:\n%s" % str(self.defs)
        r += "\nname2def: %s" % repr(self.name2def)
        if len(self.mapbind) > 0:
            r += "\nmapbind: %s" % repr(self.mapbind)
        return r

    def get_def(self, name: str) -> Define:
        return self.name2def[name]

    def add_bind(self, src):
        bid = id(src)
        if bid not in self.mapbind:
            self.mapbind[bid] = src

    def add_BU_cnt(self, src):
        self.bottom_up.append(id(src))

    def add_TD_cnt(self, src):
        self.top_down.append(id(src))

    def resolve(self):
        while True:
            do_something = False
            while True:
                if len(self.bottom_up) == 0:
                    break
                it = self.bottom_up.pop()
                b = self.mapbind[it]
                print("BU %d" % it)
                if 'to_resolve' in b.flag and b.resolvable:
                    b.unify()
                do_something = True
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
                        self.top_down.append(id(p))
                        self.bottom_up.append(id(p))
                        print("add %d" % id(p))
                    if b.dst is not None:
                        for p in b.dst:
                            self.top_down.append(id(p))
                            self.bottom_up.append(id(p))
                            print("add %d" % id(p))
                    b.flag = {'to_resolve'}
                do_something = True
            if not do_something:
                break

#####################

## for each language you must visit your tree and populate the Constraints
@meta.add_method(BlockStmt)
def populate(self, cnt: Constraints):
    print("Add %s constraint" % type(self).__name__)
    b = Bind(AnonDefine(None))
    cnt.add_bind(b)
    b.dst = []
    for it in self.body:
        b.dst.append(it.populate(cnt))
    return b

@meta.add_method(DeclVar)
def populate(self, cnt: Constraints):
    print("Add %s constraint" % type(self).__name__)
    for it in self.expr:
        it.populate(cnt)

@meta.add_method(DeclFun)
def populate(self, cnt: Constraints):
    print("Add %s constraint" % type(self).__name__)
    for it in self.block:
        it.populate(cnt)

@meta.add_method(ExprStmt)
def populate(self, cnt: Constraints):
    print("Add %s constraint" % type(self).__name__)
    return self.expr.populate(cnt)

@meta.add_method(Expr)
def populate(self, cnt: Constraints):
    print("Add %s constraint" % type(self).__name__)
    b = Bind(AnonDefine(None))
    print(b)
    cnt.add_bind(b)
    bcall = self.call_expr.populate(cnt)
    bparams = []
    for it in self.p:
        bparams.append(it.populate(cnt))
    b.src = bcall
    b.dst = bparams
    return b

@meta.add_method(Id)
def populate(self, cnt: Constraints):
    print("Add %s constraint" % type(self).__name__)
    print(self.value)
    d = cnt.get_def(self.value)
    print(d())
    b = Bind(d)
    cnt.add_bind(b)
    return b

@meta.add_method(Operator)
def populate(self, cnt: Constraints):
    print("Add %s constraint" % type(self).__name__)
    print(self.value)

@meta.add_method(Literal)
def populate(self, cnt: Constraints):
    print("Add %s constraint" % type(self).__name__)
    print(self.value)


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
        """Basic unification.
        We assume the Binding (link item to type definition is done.
        """
        def1 = Define("f", Fun(T("t1"), T("t2")))
        print(def1)
        def2 = Define("v", T("t2"))
        print(def2)
        test = TL4T()
        res = test.parse("""
            f(v);
        """)
        txt = res.to_tl4t()
        print(txt)
        cnt = Constraints([def1, def2])
        print(cnt)
        b = res.populate(cnt)
        print(cnt)
        cnt.add_TD_cnt(b)
        cnt.resolve()
