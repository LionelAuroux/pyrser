import unittest

import pdb

# TODO: move in ast
from pyrser.parsing.node import *
from pyrser.passes.to_yml import *

from pyrser.ast.state import *
from pyrser.ast.walk import *
from pyrser.ast.match import *
from pyrser.ast.psl import *

# prepare path
import os
rpath = os.path.dirname(os.path.realpath(__file__)) + os.sep + 'png'
os.makedirs(rpath, exist_ok=True)

# for validating that we go into hooks
in_test = False
class r:
    def __repr__(self) -> str:
        return str(vars(self))
class Test(r):
    pass
class A(r):
    pass
class L(list):
    def __repr__(self) -> str:
        return list.__repr__(self) + " - " + str(vars(self))
class H(dict):
    def __repr__(self) -> str:
        return dict.__repr__(self) + " - " + str(vars(self))

class InternalAst_Test(unittest.TestCase):


    def test_0_list(self):
        """ListNode tests"""
        # ListNodeItem
        l = ListNodeItem("a")
        self.assertEqual(l.prev, None, "Bad construction of l")
        self.assertEqual(l.next, None, "Bad construction of l")
        l.append("b")
        self.assertEqual(l.prev, None, "Bad construction of l")
        self.assertNotEqual(l.next, None, "Bad construction of l")
        self.assertEqual(id(l.next.prev), id(l), "Bad construction of l")
        self.assertEqual(l.next.next, None, "Bad construction of l")
        thelist = l.thelist()
        self.assertEqual(len(thelist), 2, "Bad construction of l")
        self.assertEqual(thelist.must_update, False, "Bad construction of l")
        self.assertEqual(id(thelist.begin), id(l), "Bad construction of l")
        self.assertEqual(id(thelist.begin), id(l.next.prev), "Bad construction of l")
        self.assertEqual(id(thelist.end), id(l.next), "Bad construction of l")
        self.assertEqual(thelist.begin.data, 'a', "Bad construction of l")
        self.assertEqual(thelist.end.data, 'b', "Bad construction of l")
        l.append("c")
        self.assertEqual(thelist.must_update, True, "Bad construction of l")
        self.assertEqual(len(thelist), 3, "Bad construction of l")
        self.assertEqual(thelist.must_update, False, "Bad construction of l")
        self.assertEqual(thelist.begin.data, 'a', "Bad construction of l")
        self.assertEqual(thelist.end.data, 'b', "Bad construction of l")
        self.assertEqual(thelist.begin.next.data, 'c', "Bad construction of l")
        self.assertEqual(thelist.end.prev.data, 'c', "Bad construction of l")
        self.assertEqual(l[0], 'a', "Bad construction of l")
        self.assertEqual(l[1], 'c', "Bad construction of l")
        self.assertEqual(l[2], 'b', "Bad construction of l")
        l.thelist().append('g')
        self.assertEqual(l[3], 'g', "Bad construction of l")
        self.assertEqual(l[-1], 'g', "Bad construction of l")
        self.assertEqual(l[-2], 'b', "Bad construction of l")
        self.assertEqual(l[-3], 'c', "Bad construction of l")
        self.assertEqual(l[-4], 'a', "Bad construction of l")
        with self.assertRaises(IndexError):
            l[-5] = 'g'
        subelm = []
        for it in l._fwd():
            subelm.append(it.data)
        self.assertEqual(subelm, ['a', 'c', 'b', 'g'], "Bad construction of l")
        subelm = []
        for it in l.values():
            subelm.append(it)
        self.assertEqual(subelm, ['a', 'c', 'b', 'g'], "Bad construction of l")
        subelm = []
        end = l.next.next
        for it in end._bwd():
            subelm.append(it.data)
        self.assertEqual(subelm, ['b', 'c', 'a'], "Bad construction of l")
        subelm = []
        end = l.next.next
        for it in end.rvalues():
            subelm.append(it)
        self.assertEqual(subelm, ['b', 'c', 'a'], "Bad construction of l")
        l = ListNodeItem("a")
        l.prepend("b")
        self.assertEqual(l.next, None, "Bad construction of l")
        self.assertNotEqual(l.prev, None, "Bad construction of l")
        self.assertEqual(id(l.prev.next), id(l), "Bad construction of l")
        self.assertEqual(l.prev.prev, None, "Bad construction of l")
        thelist = l.thelist()
        self.assertEqual(len(thelist), 2, "Bad construction of l")
        self.assertEqual(thelist.must_update, False, "Bad construction of l")
        self.assertEqual(id(thelist.end), id(l), "Bad construction of l")
        self.assertEqual(id(thelist.end), id(l.prev.next), "Bad construction of l")
        self.assertEqual(id(thelist.begin), id(l.prev), "Bad construction of l")
        self.assertEqual(thelist.begin.data, 'b', "Bad construction of l")
        self.assertEqual(thelist.end.data, 'a', "Bad construction of l")
        l.prepend("c")
        self.assertEqual(thelist.must_update, True, "Bad construction of l")
        self.assertEqual(len(thelist), 3, "Bad construction of l")
        self.assertEqual(thelist.must_update, False, "Bad construction of l")
        self.assertEqual(thelist.begin.data, 'b', "Bad construction of l")
        self.assertEqual(thelist.end.data, 'a', "Bad construction of l")
        self.assertEqual(thelist.begin.next.data, 'c', "Bad construction of l")
        self.assertEqual(thelist.end.prev.data, 'c', "Bad construction of l")
        self.assertEqual(l[0], 'b', "Bad construction of l")
        self.assertEqual(l[-1], 'a', "Bad construction of l")
        self.assertEqual(l[-2], 'c', "Bad construction of l")
        subelm = []
        for it in l._bwd():
            subelm.append(it.data)
        self.assertEqual(subelm, ['a', 'c', 'b'], "Bad construction of l")
        subelm = []
        for it in l.rvalues():
            subelm.append(it)
        self.assertEqual(subelm, ['a', 'c', 'b'], "Bad construction of l")
        subelm = []
        begin = l.prev.prev
        for it in begin._fwd():
            subelm.append(it.data)
        self.assertEqual(subelm, ['b', 'c', 'a'], "Bad construction of l")
        subelm = []
        begin = l.prev.prev
        for it in begin.values():
            subelm.append(it)
        self.assertEqual(subelm, ['b', 'c', 'a'], "Bad construction of l")
        lbegin = ListNodeItem('a')
        l = lbegin
        l = l.append('b')
        l = l.append('c')
        l = l.append('d')
        l = l.append('e')
        l = l.append('f')
        idx = 0
        for it in lbegin._fwd():
            if idx == 2:
                it.popitem()
            idx += 1
        self.assertEqual(lbegin.thelist(), ['a', 'b', 'd', 'e', 'f'], "Bad construction of l")
        self.assertEqual(l.thelist().must_update, False, "Bad construction of l")
        lbegin = ListNodeItem('a')
        l = lbegin
        l = l.append('b')
        l = l.append('c')
        l = l.append('d')
        l = l.append('e')
        l = l.append('f')
        del lbegin[2]
        self.assertEqual(str(lbegin.thelist()), "['a', 'b', 'd', 'e', 'f']", "Bad construction of l")
        self.assertEqual(l.thelist().must_update, True, "Bad construction of l")
        # ListNode
        ls = ListNode()
        ls.append('a')
        self.assertEqual(ls.begin.data, 'a', "Bad construction of ls")
        self.assertEqual(ls.end.data, 'a', "Bad construction of ls")
        ls.append('b')
        self.assertEqual(ls.begin.data, 'a', "Bad construction of ls")
        self.assertEqual(ls.end.data, 'b', "Bad construction of ls")
        ls.append('c')
        self.assertEqual(ls.begin.data, 'a', "Bad construction of ls")
        self.assertEqual(ls.begin.next.data, 'b', "Bad construction of ls")
        self.assertEqual(ls.end.prev.data, 'b', "Bad construction of ls")
        self.assertEqual(ls.end.data, 'c', "Bad construction of ls")
        self.assertEqual(ls.must_update, True, "Bad construction of ls")
        self.assertEqual(len(ls), 3, "Bad construction of ls")
        self.assertEqual(ls.must_update, False, "Bad construction of ls")
        self.assertEqual(len(ls.cache), 3, "Bad construction of ls")
        self.assertEqual(ls[0], 'a', "Bad construction of ls")
        self.assertEqual(ls[1], 'b', "Bad construction of ls")
        self.assertEqual(ls[2], 'c', "Bad construction of ls")
        ls = ListNode()
        ls.prepend('c')
        self.assertEqual(ls.must_update, True, "Bad construction of ls")
        self.assertNotEqual(ls.begin, None, "Bad construction of ls")
        self.assertNotEqual(ls.end, None, "Bad construction of ls")
        ls.prepend('b')
        ls.prepend('a')
        self.assertEqual(len(ls), 3, "Bad construction of ls")
        self.assertEqual(ls.must_update, False, "Bad construction of ls")
        self.assertEqual(ls[0], 'a', "Bad construction of ls")
        self.assertEqual(ls.must_update, False, "Bad construction of ls")
        ls.append('d')
        self.assertEqual(len(ls), 4, "Bad construction of ls")
        self.assertEqual(ls[1], 'b', "Bad construction of ls")
        self.assertEqual(ls[2], 'c', "Bad construction of ls")
        self.assertEqual(ls[3], 'd', "Bad construction of ls")
        # ListNode vs list
        ls = ListNode([1, 2, 3, 4, 5, 6])
        self.assertEqual(len(ls), 6, "Bad construction of ls")
        ls2 = list(ls)
        self.assertEqual(ls2, [1, 2, 3, 4, 5, 6], "Bad construction of ls")
        ls3 = list(reversed(ls))
        self.assertEqual(ls3, [6, 5, 4, 3, 2, 1], "Bad construction of ls")
        node = ls.get(3)
        self.assertEqual(node.data, 4, "Bad construction of ls")
        self.assertEqual(node.next.data, 5, "Bad construction of ls")
        self.assertEqual(node.prev.data, 3, "Bad construction of ls")
        # slice
        s1 = ls[4:]
        self.assertEqual(s1, [1, 2, 3, 4, 5, 6][4:], "Bad slice of ls")
        # del
        del ls[3]
        self.assertEqual(ls[3], 5, "Bad construction of ls")
        self.assertEqual(id(ls.get(3).prev), id(ls.get(2)), "Bad construction of ls")
        self.assertEqual(id(ls.get(3).next), id(ls.get(4)), "Bad construction of ls")
        self.assertEqual(id(ls.get(2).next), id(ls.get(3)), "Bad construction of ls")
        self.assertEqual(id(ls.get(4).prev), id(ls.get(3)), "Bad construction of ls")
        sz = len(ls) - 1
        del ls[sz]
        sz -= 1
        self.assertEqual(ls[sz], 5, "Bad construction of ls")
        self.assertEqual(id(ls.get(sz).next), id(None), "Bad construction of ls")


    def test_1_normalize(self):
        tree = {'a': 12, 'b':[2, 3, 5, 'tata'], 'c':'toto'}
        tree = normalize(tree)
        self.assertIs(type(tree), DictNode, "Bad normalization of Dict")
        self.assertIs(type(tree['b']), ListNode, "Bad normalization of Dict")
        match(tree)

    def test_2_match_classes(self):
        # []
        m = MatchList([MatchIndice(1, MatchValue(12)), MatchIndice(3, MatchValue('toto')), MatchIndice(5, MatchValue(13))], strict=False)
        r = "[1: 12, 3: 'toto', 5: 13, ...]"
        self.assertEqual(str(m), r, "Can't format MatchList")
        # {}
        m = MatchDict([MatchKey('a', MatchValue(12)), MatchKey('b', MatchValue('toto')), MatchKey('c', MatchValue(13))], strict=False)
        r = "{'a': 12, 'b': 'toto', 'c': 13, ...}"
        self.assertEqual(str(m), r, "Can't format MatchDict")
        # type base
        m = MatchType(A, [MatchAttr('a', MatchValue('toto')), MatchAttr('b', MatchValue(12)), MatchAttr('c', MatchValue('lolo'))], strict=False)
        r = "A(.a='toto', .b=12, .c='lolo', ...)"
        self.assertEqual(str(m), r, "Can't format MatchType")
        # type list
        m = MatchType(A, subs=MatchList([MatchIndice(1, MatchValue(12)), MatchIndice(3, MatchValue('toto')), MatchIndice(5, MatchValue(13))], strict=False), strict=False)
        r = "A([1: 12, 3: 'toto', 5: 13, ...] ...)"
        self.assertEqual(str(m), r, "Can't format MatchType")
        # type dict
        m = MatchType(A, subs=MatchDict([MatchKey('a', MatchValue(12)), MatchKey('b', MatchValue('toto')), MatchKey('c', MatchValue(13))], strict=False), strict=False)
        r = "A({'a': 12, 'b': 'toto', 'c': 13, ...} ...)"
        self.assertEqual(str(m), r, "Can't format MatchType")
        # -> hook
        def hook():
            pass
        m = MatchHook(hook, MatchType(A, [MatchAttr('a', MatchValue('toto')), MatchAttr('b', MatchValue(12)), MatchAttr('c', MatchValue('lolo'))], strict=False))
        r = "A(.a='toto', .b=12, .c='lolo', ...) -> #hook;"
        self.assertEqual(str(m), r, "Can't format MatchHook")
        # BLOCK
        m = MatchBlock([MatchHook(hook, MatchType(A, [MatchAttr('a', MatchValue('toto')), MatchAttr('b', MatchValue(12)), MatchAttr('c', MatchValue('lolo'))], strict=False))])
        r = "{\n    A(.a='toto', .b=12, .c='lolo', ...) -> #hook;\n}"
        self.assertEqual(str(m), r, "Can't format MatchBlock")

    def test_3_match_tree_event(self):
        def hook1():
            pass
        def hook2():
            pass
        m = MatchBlock([
            MatchHook(hook1, MatchType(A, [MatchAttr('a', MatchValue('toto')),
                                            MatchAttr('b', MatchValue(12)),
                                            MatchAttr('c', MatchValue('lolo'))], strict=False)),
            MatchHook(hook2, MatchType(A, [MatchAttr('a', MatchValue('toto')),
                                            MatchAttr('b', MatchValue(12)),
                                            MatchAttr('d', MatchValue('lolo'))], strict=False)),
            ])
        tree = []
        m.get_match_tree(tree)
        self.assertEqual(len(tree), 4, "Bad tree construction")
        self.assertEqual(tree[1][0][1], 'A', "Bad tree construction")
        self.assertEqual(len(tree[2]), 2, "Bad tree construction")
        self.assertEqual(len(tree[3]), 2, "Bad tree construction")
        self.assertEqual(len(tree[0]), 2, "Bad tree construction")

    def test_4_psl_syntax(self):
        class A:
            pass
        def hook1():
            pass
        def hook2():
            pass
        p = PSL()
        p.set_psl_hooks({'hook1': hook1, 'hook2': hook2})
        p.set_psl_types({'A': A})
        res = p.parse("""
            {
                A(.a='toto', .c='lolo', .b=12) -> #hook1;
            }
        """)
        self.assertEqual(type(res.node), MatchBlock, "Bad parsing of PSL expression")
        self.assertEqual(type(res.node.stmts[0]), MatchHook, "Bad parsing of PSL expression")
        self.assertEqual(type(res.node.stmts[0].v), MatchType, "Bad parsing of PSL expression")
        self.assertEqual(type(res.node.stmts[0].v.attrs[0]), MatchAttr, "Bad parsing of PSL expression")
        self.assertEqual(res.node.stmts[0].v.attrs[0].name, 'a', "Bad parsing of PSL expression")
        self.assertEqual(type(res.node.stmts[0].v.attrs[0].v), MatchValue, "Bad parsing of PSL expression")
        self.assertEqual(res.node.stmts[0].v.attrs[0].v.v, 'toto', "Bad parsing of PSL expression")
        tree = []
        res.node.get_match_tree(tree)
        print(to_yml(tree))
