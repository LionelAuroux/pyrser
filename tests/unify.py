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
    def __init__(self, ast_node, cnt: 'Constraints'):
        self.ast_node = ast_node
        self.cnt = cnt
        # top-down dependence on another Bind object
        # top-down dependence on another Bind object
        self.td_depend = None
        # bottom-up dependence on another Bind object
        self.bu_depend = None
        self.final_type = None
        self.flag = {'to_visit'}

    @staticmethod
    def createList(cnt: 'Constraints', parent_bind: 'Bind', size: int) -> ['Bind']:
        res = []
        lastid = cnt.get_id_by_bind(parent_bind)
        for it in range(size):
            b = Bind(None, cnt)
            b.bu_depend = lastid
            bid = cnt.get_id_by_bind(b)
            cnt.get_bind_by_id(lastid).td_depend = bid
            lastid = bid
            res.append(b)
        return res

    @staticmethod
    def bu_walk(b: 'Bind'):
        cnt = b.cnt
        bid = cnt.get_id_by_bind(b)
        nid = b.bu_depend
        while True:
            yield (bid, nid)
            if nid is not None:
                b = cnt.get_bind_by_id(nid)
                bid = id(b)
                nid = b.bu_depend
            else:
                break

    @staticmethod
    def td_walk(b: 'Bind'):
        cnt = b.cnt
        bid = cnt.get_id_by_bind(b)
        nid = b.td_depend
        while True:
            yield (bid, nid)
            if nid is not None:
                b = cnt.get_bind_by_id(nid)
                bid = id(b)
                nid = b.td_depend
            else:
                break

    def __str__(self) -> str:
        r = "\nid: %d" % id(self)
        r += "\nflags: %s" % str(self.flag)
        if self.bu_depend is not None:
            r += "\nbu_depend: %d" % self.bu_depend
        if self.td_depend is not None:
            r += "\ntd_depend: %d" % self.td_depend
        print("\n")
        return r
    
    def __repr__(self) -> str:
        return str(self)

    def unify(self):
        print("Unify %s" % self.ast_node.to_tl4t())
        return True

class Constraints:
    def __init__(self, initial_defs: [Define]=None):
        # store definitions
        self.defs = []
        # map name -> idx in defs
        self.name2id = ChainMap()
        if initial_defs is not None:
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
            r += "\nmapbind:\n"
            r += "{\n"
            for k in sorted(self.mapbind.keys()):
                r += "\t%d: %s\n" % (k, self.mapbind[k])
            r += "}\n"
        return r

    def get_def(self, name: str) -> Define:
        return self.defs[self.name2id[name]]

    def get_bind_by_id(self, bid: int) -> Bind:
        return self.mapbind[bid]

    def get_id_by_bind(self, src) -> int:
        bid = id(src)
        if bid not in self.mapbind:
            self.mapbind[bid] = src
        return bid

    def add_BU_cnt(self, src) -> int:
        id_src = self.get_id_by_bind(src)
        self.bottom_up.append(id_src)
        return id_src

    def add_TD_cnt(self, src):
        id_src = self.get_id_by_bind(src)
        self.top_down.append(id_src)
        return id_src

    def resolve(self):
        while True:
            done_something = False
            # BU
            while True:
                if len(self.bottom_up) == 0:
                    break
                it = self.bottom_up.pop()
                b = self.mapbind[it]
                print("BU %d - %s" % (it, b.ast_node))
                if 'to_resolve' in b.flag:
                    if b.unify():
                        if b.bu_depend is not None:
                            self.bottom_up.append(b.bu_depend)
                        b.flag = {'to_resolve'}
                    done_something = True
            # TD
            while True:
                if len(self.top_down) == 0:
                    break
                it = self.top_down.pop()
                b = self.mapbind[it]
                print("TD %d - %s" % (it, b.ast_node))
                if 'to_visit' in b.flag:
                    if b.unify():
                        if b.td_depend is not None:
                            self.top_down.append(b.td_depend)
                        b.flag = {'to_resolve'}
                    done_something = True
            if not done_something:
                break

#####################

## for each language you must visit your tree and populate the Constraints
## Create a Bind object and add it in the contraint object
## Add a TD if need
@meta.add_method(BlockStmt)
def populate(self, cnt: Constraints, parent_bind: 'Bind'):
    print("Add %s constraint" % type(self).__name__)
    cnt.push_context()
    len_lst = len(self.body)
    sub = Bind.createList(cnt, parent_bind, len_lst)
    parent_bind.ast_node = self
    bid = cnt.add_TD_cnt(parent_bind)
    for idx, it in zip(range(len_lst), self.body):
        it.populate(cnt, sub[idx])
    parent_bind.td_depend = cnt.get_id_by_bind(sub[0])
    sub[0].bu_depend = cnt.get_id_by_bind(bid)
    cnt.pop_context()

@meta.add_method(DeclVar)
def populate(self, cnt: Constraints, parent_bind: 'Bind'):
    print("Add %s constraint" % type(self).__name__)
    d = Define(self.name, T(self.t))
    cnt.add_defines([d])
    sub = Bind.createList(cnt, parent_bind, 1)
    parent_bind.ast_node = self
    down_id = self.expr.populate(cnt, sub[0])
    bid = cnt.add_TD_cnt(parent_bind)
    parent_bind.td_depend = cnt.get_id_by_bind(sub[0])
    cnt.get_bind_by_id(down_id).bu_depend = bid
    return bid
    

@meta.add_method(DeclFun)
def populate(self, cnt: Constraints, parent_bind: 'Bind'):
    print("Add %s constraint" % type(self).__name__)
    # TODO: namespace/parametric/variadic...
    # voir td_depend et bu_depend
    d = Define(self.name, Fun(T(self.t, *self.p)))
    cnt.add_defines([d])
    len_lst = len(self.block)
    sub = Bind.createList(cnt, parent_bind, len_lst)
    parent_bind.ast_node = self
    bid = cnt.add_TD_cnt(parent_bind)
    for idx, it in zip(range(len_lst), self.block):
        it.populate(cnt, sub[idx])
    parent_bind.td_depend = cnt.get_id_by_bind(sub[0])
    sub[0].bu_depend = cnt.get_id_by_bind(bid)
    return bid

@meta.add_method(ExprStmt)
def populate(self, cnt: Constraints, parent_bind: 'Bind'):
    print("Add %s constraint" % type(self).__name__)
    return self.expr.populate(cnt, parent_bind)

@meta.add_method(Expr)
def populate(self, cnt: Constraints, parent_bind: 'Bind'):
    print("Add %s constraint" % type(self).__name__)
    len_lst = len(self.p)
    sub = Bind.createList(cnt, parent_bind, len_lst + 1)
    parent_bind.ast_node = self
    bid = cnt.add_TD_cnt(parent_bind)
    down_id = self.call_expr.populate(cnt, sub[0])
    # TODO: must do a Bind for return?
    for idx, it in zip(range(1, len_lst + 1), self.p):
        it.populate(cnt, sub[idx])
    parent_bind.td_depend = cnt.get_id_by_bind(sub[0])
    sub[0].bu_depend = cnt.get_id_by_bind(bid)
    return bid

@meta.add_method(Id)
def populate(self, cnt: Constraints, parent_bind: 'Bind'):
    print("Add %s constraint" % type(self).__name__)
    print(self.value)
    parent_bind.ast_node = self
    # TODO: Found the definition of self.value
    bid = cnt.add_BU_cnt(parent_bind)
    parent_bind.bu_depend = bid
    return bid

@meta.add_method(Operator)
def populate(self, cnt: Constraints, parent_bind: 'Bind'):
    print("Add %s constraint" % type(self).__name__)
    print(self.value)
    parent_bind.ast_node = self
    # TODO: Found the definition of operator
    bid = cnt.add_BU_cnt(parent_bind)
    parent_bind.bu_depend = bid
    return bid

@meta.add_method(Literal)
def populate(self, cnt: Constraints, parent_bind: 'Bind'):
    print("Add %s constraint" % type(self).__name__)
    print(self.value)
    parent_bind.ast_node = self
    # TODO: Found the type of the literal
    bid = cnt.add_BU_cnt(parent_bind)
    parent_bind.bu_depend = bid
    return bid

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
        """Bind object and list
        """
        cnt = Constraints()
        b = Bind(None, cnt)
        lstb = Bind.createList(cnt, b, 5)
        self.assertEqual(b.td_depend, id(lstb[0]), "List return by createList seems buggy")
        self.assertEqual(id(b), lstb[0].bu_depend, "List return by createList seems buggy")
        self.assertEqual(lstb[0].td_depend, id(lstb[1]), "List return by createList seems buggy")
        self.assertEqual(id(lstb[0]), lstb[1].bu_depend, "List return by createList seems buggy")
        self.assertEqual(lstb[1].td_depend, id(lstb[2]), "List return by createList seems buggy")
        self.assertEqual(id(lstb[1]), lstb[2].bu_depend, "List return by createList seems buggy")
        self.assertEqual(lstb[2].td_depend, id(lstb[3]), "List return by createList seems buggy")
        self.assertEqual(id(lstb[2]), lstb[3].bu_depend, "List return by createList seems buggy")
        self.assertEqual(lstb[3].td_depend, id(lstb[4]), "List return by createList seems buggy")
        self.assertEqual(id(lstb[3]), lstb[4].bu_depend, "List return by createList seems buggy")
        self.assertEqual(lstb[4].td_depend, None, "List return by createList seems buggy")
        lsbu = list(Bind.bu_walk(lstb[-1]))
        lsburef = []
        what = lstb[-1]
        while what is not None:
            (bid, nid) = (id(what), what.bu_depend)
            lsburef.append((bid, nid))
            if nid is not None:
                what = what.cnt.get_bind_by_id(nid)
            else:
                what = None
        self.assertEqual(lsbu, lsburef, "List walked by bu_walk seems buggy")
        lstd = list(Bind.td_walk(b))
        lstdref = []
        what = b
        while what is not None:
            (bid, nid) = (id(what), what.td_depend)
            lstdref.append((bid, nid))
            if nid is not None:
                what = what.cnt.get_bind_by_id(nid)
            else:
                what = None
        self.assertEqual(lstd, lstdref, "List walked by bu_walk seems buggy")
        # Test it with a little grammar
        test = TL4T()
        res = test.parse("""
            v = f(a, b, c, d);
        """)
        # get AST nodes
        blockstmt = res
        exprstmt = blockstmt.body[0]
        eqexpr = exprstmt.expr
        eq = eqexpr.call_expr
        self.assertEqual(eq.value, '=', "bad access to parameter")
        v = eqexpr.p[0]
        self.assertEqual(v.value, 'v', "bad access to parameter")
        funexpr = eqexpr.p[1]
        f = funexpr.call_expr
        self.assertEqual(f.value, 'f', "bad access to parameter")
        a = funexpr.p[0]
        self.assertEqual(a.value, 'a', "bad access to parameter")
        b = funexpr.p[1]
        self.assertEqual(b.value, 'b', "bad access to parameter")
        c = funexpr.p[2]
        self.assertEqual(c.value, 'c', "bad access to parameter")

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
        b = Bind(None, cnt)
        idb = res.populate(cnt, b)
        print(cnt)
        print('###################')
        cnt.resolve()
        print('###################')
