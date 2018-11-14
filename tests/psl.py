import unittest

import pdb

# TODO: move in ast
from pyrser.parsing.node import *
from pyrser.passes.to_yml import *

from pyrser.ast.walk import *
from pyrser.ast.match import *
from pyrser.ast.stack_action import *
from pyrser.ast.psl import *

# prepare path
import os
rpath = os.path.dirname(os.path.realpath(__file__)) + os.sep + 'png'
os.makedirs(rpath, exist_ok=True)

###
class A:
    def __init__(self, *item, **k):
        self._is_list = False
        self._is_dict = False
        self._have_attr = False
        for it in item:
            if type(it) is list:
                self._l = it
                self._is_list = True
            if type(it) is dict:
                self._d = it
                self._is_dict = True
        if k is not None:
            self.__dict__.update(k)
            self._have_attr = True
    def __repr__(self):
        lsres = []
        if self._is_list:
            lsres.append(repr(self._l))
        if self._is_dict:
            lsres.append(repr(self._d))
        if self._have_attr:
           lsres += ["%s=%s" % (k, repr(v)) for k, v in vars(self).items() if k[0] != '_']
        return "%s(%s)" % (type(self).__name__, ', '.join(lsres))

class B(A): pass
class C(A): pass
class D(A): pass

def hook1(capture, user_data):
    user_data.nbhook += 1
    user_data.assertIn('a', capture, "Not captured")
    user_data.assertIn('b', capture, "Not captured")
    a = capture['a']
    b = capture['b']
    user_data.assertEqual(b, 12, "Not captured")

def hook_count(capture, user_data):
    user_data.nbhook += 1

def test1(capture, user_data):
    a = capture['a']
    user_data.append(a)

def testlist(capture, user_data):
    a = capture['a']
    user_data += a

def testdict(capture, user_data):
    a = capture['a']
    user_data.clear()
    user_data.extend(a)

def testcopy(capture, user_data):
    user_data.append(capture.copy())
###


class PSL_Test(unittest.TestCase):


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
        m = MatchType('A', [MatchAttr('a', MatchValue('toto')), MatchAttr('b', MatchValue(12)), MatchAttr('c', MatchValue('lolo'))], strict=False)
        r = "A(.a='toto', .b=12, .c='lolo', ...)"
        self.assertEqual(str(m), r, "Can't format MatchType")
        # type base instanceof
        m = MatchType('A', [MatchAttr('a', MatchValue('toto')), MatchAttr('b', MatchValue(12)), MatchAttr('c', MatchValue('lolo'))], strict=False, iskindof=True)
        r = "A?(.a='toto', .b=12, .c='lolo', ...)"
        self.assertEqual(str(m), r, "Can't format MatchType")
        # type list
        m = MatchType('A', subs=MatchList([MatchIndice(1, MatchValue(12)), MatchIndice(3, MatchValue('toto')), MatchIndice(5, MatchValue(13))], strict=False), strict=False)
        r = "A([1: 12, 3: 'toto', 5: 13, ...] ...)"
        self.assertEqual(str(m), r, "Can't format MatchType")
        # type dict
        m = MatchType('A', subs=MatchDict([MatchKey('a', MatchValue(12)), MatchKey('b', MatchValue('toto')), MatchKey('c', MatchValue(13))], strict=False), strict=False)
        r = "A({'a': 12, 'b': 'toto', 'c': 13, ...} ...)"
        self.assertEqual(str(m), r, "Can't format MatchType")
        # => #hook
        m = MatchHook('hook', MatchType('A', [MatchAttr('a', MatchValue('toto')), MatchAttr('b', MatchValue(12)), MatchAttr('c', MatchValue('lolo'))], strict=False))
        r = "A(.a='toto', .b=12, .c='lolo', ...) => #hook;"
        self.assertEqual(str(m), r, "Can't format MatchHook")
        # => Event
        m = MatchEvent('Event', MatchType('A', [MatchAttr('a', MatchValue('toto')), MatchAttr('b', MatchValue(12)), MatchAttr('c', MatchValue('lolo'))], strict=False))
        r = "A(.a='toto', .b=12, .c='lolo', ...) => Event;"
        self.assertEqual(str(m), r, "Can't format MatchEvent")
        # PrecondEvent
        m = MatchPrecond(PrecondEvent('Event'), MatchType('A', [MatchAttr('a', MatchValue('toto')), MatchAttr('b', MatchValue(12)), MatchAttr('c', MatchValue('lolo'))], strict=False))
        r = "A(.a='toto', .b=12, .c='lolo', ...) && (Event)"
        self.assertEqual(str(m), r, "Can't format PrecondEvent")
        # PrecondEvent no clean
        m = MatchPrecond(PrecondEvent('Event'), MatchType('A', [MatchAttr('a', MatchValue('toto')), MatchAttr('b', MatchValue(12)), MatchAttr('c', MatchValue('lolo'))], strict=False), clean_event=False)
        r = "A(.a='toto', .b=12, .c='lolo', ...) !! (Event)"
        self.assertEqual(str(m), r, "Can't format PrecondEvent")
        # PrecondAnd
        m = MatchPrecond(PrecondAnd(PrecondEvent('Event1'), PrecondEvent('Event2')), MatchType('A', [MatchAttr('a', MatchValue('toto')), MatchAttr('b', MatchValue(12)), MatchAttr('c', MatchValue('lolo'))], strict=False))
        r = "A(.a='toto', .b=12, .c='lolo', ...) && (Event1 & Event2)"
        self.assertEqual(str(m), r, "Can't format PrecondAnd")
        # PrecondOr
        m = MatchPrecond(PrecondOr(PrecondEvent('Event1'), PrecondEvent('Event2')), MatchType('A', [MatchAttr('a', MatchValue('toto')), MatchAttr('b', MatchValue(12)), MatchAttr('c', MatchValue('lolo'))], strict=False))
        r = "A(.a='toto', .b=12, .c='lolo', ...) && (Event1 | Event2)"
        self.assertEqual(str(m), r, "Can't format PrecondOr")
        # PrecondXor
        m = MatchPrecond(PrecondXor(PrecondEvent('Event1'), PrecondEvent('Event2')), MatchType('A', [MatchAttr('a', MatchValue('toto')), MatchAttr('b', MatchValue(12)), MatchAttr('c', MatchValue('lolo'))], strict=False))
        r = "A(.a='toto', .b=12, .c='lolo', ...) && (Event1 ^ Event2)"
        self.assertEqual(str(m), r, "Can't format PrecondXor")
        # PrecondNot
        m = MatchPrecond(PrecondNot(PrecondEvent('Event')), MatchType('A', [MatchAttr('a', MatchValue('toto')), MatchAttr('b', MatchValue(12)), MatchAttr('c', MatchValue('lolo'))], strict=False))
        r = "A(.a='toto', .b=12, .c='lolo', ...) && (!Event)"
        self.assertEqual(str(m), r, "Can't format PrecondNot")
        # PrecondParen
        m = MatchPrecond(PrecondParen(PrecondEvent('Event')), MatchType('A', [MatchAttr('a', MatchValue('toto')), MatchAttr('b', MatchValue(12)), MatchAttr('c', MatchValue('lolo'))], strict=False))
        r = "A(.a='toto', .b=12, .c='lolo', ...) && ((Event))"
        self.assertEqual(str(m), r, "Can't format PrecondEvent")
        # BLOCK
        m = MatchBlock([MatchHook('hook', MatchCapture('y', MatchType('A', [MatchAttr('a', MatchCapture('x', MatchValue('toto'))), MatchAttr('b', MatchValue(12)), MatchAttr('c', MatchValue('lolo'))], strict=False)))])
        r = "{\n    A(.a='toto'->x, .b=12, .c='lolo', ...)->y => #hook;\n}"
        self.assertEqual(str(m), r, "Can't format MatchBlock")
        # Ancestor
        m = MatchBlock([MatchHook('hook', MatchAncestor(MatchAncestor(MatchType('A', strict=False), MatchType('B', strict=False)), MatchType('C', strict=False)))])
        r = "{\n    A(...) / B(...) / C(...) => #hook;\n}"
        self.assertEqual(str(m), r, "Can't format MatchAncestor")
        m = MatchBlock([MatchHook('hook', MatchAncestor(MatchAncestor(MatchType('A', strict=False), MatchType('B', strict=False), 3), MatchType('C', strict=False), 2, True))])
        r = "{\n    A(...) /3 B(...) /+2 C(...) => #hook;\n}"
        self.assertEqual(str(m), r, "Can't format MatchAncestor")
        m = MatchBlock([MatchHook('hook', MatchAncestor(MatchSibling(MatchType('A', strict=False), MatchType('B', strict=False)), MatchType('C', strict=False), 2, True))])
        r = "{\n    < A(...) ~~ B(...) > /+2 C(...) => #hook;\n}"
        self.assertEqual(str(m), r, "Can't format MatchAncestor")

    def test_3_match_tree_event(self):
        m = MatchBlock([
            MatchHook('hook1', MatchType(A, [MatchAttr('a', MatchValue('toto')),
                                            MatchAttr('b', MatchValue(12)),
                                            MatchAttr('c', MatchValue('lolo'))], strict=False)),
            MatchHook('hook2', MatchType(A, [MatchAttr('a', MatchValue('toto')),
                                            MatchAttr('b', MatchValue(12)),
                                            MatchAttr('d', MatchValue('lolo'))], strict=False)),
            ])
        tree = m.get_stack_action()
        self.assertEqual(len(tree), 2, "Can't get a good stack action len")

    def test_4_psl_syntax(self):
        class A:
            pass
        def hook1():
            pass
        def hook2():
            pass
        # Basic syntax
        p = PSL()
        res = p.parse("""
            {
                A(.a='toto'->x, .c='lolo', .b=12)->y => #hook1;
            }
        """)
        self.assertEqual(type(res.node[0]), MatchBlock, "Bad parsing of PSL expression")
        self.assertEqual(type(res.node[0].stmts[0]), MatchHook, "Bad parsing of PSL expression")
        self.assertEqual(type(res.node[0].stmts[0].v), MatchCapture, "Bad parsing of PSL expression")
        self.assertEqual(type(res.node[0].stmts[0].v.v.attrs[0]), MatchAttr, "Bad parsing of PSL expression")
        self.assertEqual(res.node[0].stmts[0].v.v.attrs[0].name, 'a', "Bad parsing of PSL expression")
        self.assertEqual(type(res.node[0].stmts[0].v.v.attrs[0].v.v), MatchValue, "Bad parsing of PSL expression")
        self.assertEqual(res.node[0].stmts[0].v.v.attrs[0].v.v.v, 'toto', "Bad parsing of PSL expression")
        tree = res.node[0].get_stack_action()
        # iskindof type
        p = PSL()
        res = p.parse("""
            {
                A?(.a=*, ...) => #hook1;
            }
        """)
        self.assertIs(res.node[0].stmts[0].v.iskindof, True, "Can't see the iskindof")
        # wildcard on value
        p = PSL()
        res = p.parse("""
            {
                A(.a=*, ...) => #hook1;
            }
        """)
        self.assertIs(res.node[0].stmts[0].v.attrs[0].v.v, None, "Can't see the star")
        self.assertEqual(res.node[0].stmts[0].v.strict, False, "Can't see the ellipsis")
        # wildcard on list
        res = p.parse("""
            {
                A([*:* , ...] ...) => #hook1;
            }
        """)
        self.assertIs(res.node[0].stmts[0].v.attrs, None, "Can't see the ellipsis")
        self.assertEqual(res.node[0].stmts[0].v.strict, False, "Can't see the ellipsis")
        self.assertIs(type(res.node[0].stmts[0].v.subs), MatchList, "Can't see the ellipsis")
        self.assertIs(res.node[0].stmts[0].v.subs.ls[0].idx, None, "Can't see the star")
        self.assertIs(res.node[0].stmts[0].v.subs.ls[0].v.v, None, "Can't see the star")
        # wildcard on dict
        res = p.parse("""
            {
                A({*:* , ...} ...) => #hook1;
            }
        """)
        self.assertIs(res.node[0].stmts[0].v.attrs, None, "Can't see the ellipsis")
        self.assertEqual(res.node[0].stmts[0].v.strict, False, "Can't see the ellipsis")
        self.assertIs(type(res.node[0].stmts[0].v.subs), MatchDict, "Can't see the ellipsis")
        self.assertIs(res.node[0].stmts[0].v.subs.d[0].key, None, "Can't see the star")
        self.assertIs(res.node[0].stmts[0].v.subs.d[0].v.v, None, "Can't see the star")
        # ancestors
        res = p.parse("""
            {
                A(...) / B(...) /+2 C(...) /3 D(...) => #hook1;
            }
        """)
        self.assertIs(type(res.node[0].stmts[0].v), MatchAncestor, "Can't see the ancestor")
        self.assertEqual(res.node[0].stmts[0].v.depth, 3, "Can't see the depth")
        self.assertFalse(res.node[0].stmts[0].v.is_min, "Can't see the is_min")
        self.assertIs(type(res.node[0].stmts[0].v.left), MatchAncestor, "Can't see the ancestor")
        self.assertEqual(res.node[0].stmts[0].v.left.depth, 2, "Can't see the depth")
        self.assertTrue(res.node[0].stmts[0].v.left.is_min, "Can't see the is_min")
        self.assertIs(type(res.node[0].stmts[0].v.left.left), MatchAncestor, "Can't see the ancestor")
        self.assertEqual(res.node[0].stmts[0].v.left.left.depth, 1, "Can't see the depth")
        self.assertFalse(res.node[0].stmts[0].v.left.left.is_min, "Can't see the is_min")
        self.assertIs(type(res.node[0].stmts[0].v.left.right), MatchType, "Can't see the ancestor")
        # siblings
        res = p.parse("""
            {
                A(...) ~~ B(...) ~~ C(...) ~~ D(...) => #hook1;
            }
        """)
        self.assertIs(type(res.node[0].stmts[0].v), MatchSibling, "Can't see the sibling")
        self.assertIs(type(res.node[0].stmts[0].v.ls[0]), MatchType, "Can't see the type")
        self.assertIs(type(res.node[0].stmts[0].v.ls[1]), MatchType, "Can't see the type")
        self.assertIs(type(res.node[0].stmts[0].v.ls[2]), MatchType, "Can't see the type")
        self.assertIs(type(res.node[0].stmts[0].v.ls[3]), MatchType, "Can't see the type")
        self.assertEqual(res.node[0].stmts[0].v.ls[0].t, 'A', "Can't see the type A")
        self.assertEqual(res.node[0].stmts[0].v.ls[1].t, 'B', "Can't see the type B")
        self.assertEqual(res.node[0].stmts[0].v.ls[2].t, 'C', "Can't see the type C")
        self.assertEqual(res.node[0].stmts[0].v.ls[3].t, 'D', "Can't see the type D")
        # mix ancestors/siblings with <> for priority
        res = p.parse("""
            {
                A(...) ~~ < B(...) / C(...) > ~~ D(...) => #hook1;
            }
        """)
        self.assertIs(type(res.node[0].stmts[0].v), MatchSibling, "Can't see the sibling")
        self.assertIs(type(res.node[0].stmts[0].v.ls[0]), MatchType, "Can't see the sibling")
        self.assertIs(type(res.node[0].stmts[0].v.ls[1]), MatchAncestor, "Can't see the type")
        self.assertIs(type(res.node[0].stmts[0].v.ls[2]), MatchType, "Can't see the type")
        self.assertEqual(res.node[0].stmts[0].v.ls[0].t, 'A', "Can't see the A")
        self.assertEqual(res.node[0].stmts[0].v.ls[1].left.t, 'B', "Can't see the B")
        self.assertEqual(res.node[0].stmts[0].v.ls[1].right.t, 'C', "Can't see the C")
        self.assertEqual(res.node[0].stmts[0].v.ls[2].t, 'D', "Can't see the D")
        # event & PrecondEvent
        res = p.parse("""
            {
                A(...) && (Event1) => Event2;
            }
        """)
        self.assertIs(type(res.node[0].stmts[0].v), MatchPrecond, "Can't see MatchPrecond")
        self.assertIs(type(res.node[0].stmts[0].v.precond), PrecondEvent, "Can't see PrecondEvent")
        # event & PrecondNot
        res = p.parse("""
            {
                A(...) && (!Event1) => Event2;
            }
        """)
        self.assertIs(type(res.node[0].stmts[0].v), MatchPrecond, "Can't see MatchPrecond")
        self.assertIs(type(res.node[0].stmts[0].v.precond), PrecondNot, "Can't see PrecondNot")
        # event & PrecondParen
        res = p.parse("""
            {
                A(...) && ((Event1)) => Event2;
            }
        """)
        self.assertIs(type(res.node[0].stmts[0].v), MatchPrecond, "Can't see MatchPrecond")
        self.assertIs(type(res.node[0].stmts[0].v.precond), PrecondParen, "Can't see PrecondParen")
        # event & PrecondOr
        res = p.parse("""
            {
                A(...) && (Event1 | Event2) => Event3;
            }
        """)
        self.assertIs(type(res.node[0].stmts[0].v), MatchPrecond, "Can't see MatchPrecond")
        self.assertIs(type(res.node[0].stmts[0].v.precond), PrecondOr, "Can't see PrecondOr")
        # event & PrecondAnd
        res = p.parse("""
            {
                A(...) && (Event1 & Event2) => Event3;
            }
        """)
        self.assertIs(type(res.node[0].stmts[0].v), MatchPrecond, "Can't see MatchPrecond")
        self.assertIs(type(res.node[0].stmts[0].v.precond), PrecondAnd, "Can't see PrecondAnd")
        # event & PrecondXor
        res = p.parse("""
            {
                A(...) && (Event1 ^ Event2) => Event3;
            }
        """)
        self.assertIs(type(res.node[0].stmts[0].v), MatchPrecond, "Can't see MatchPrecond")
        self.assertIs(type(res.node[0].stmts[0].v.precond), PrecondXor, "Can't see PrecondXor")

    def test_5_stack_basic(self):
        class A:
            pass
        # stack for matching: A(.a=12)
        stack = [[
            [(0, 0), # block id, stmt id
                [
                    [('value', 12), ('type', 'int'), ('capture', 'b'), ('end_node', ), ('store_ancestor_depth', 0), ('attr', 'a'), ('set_event', 0)],
                    [
                        ('end_attrs', ),
                        ('check_attr_len', 1),
                        ('value', ),
                        ('type', 'A'),
                        ('capture', 'a'),
                        ('end_node', ),
                        ('check_ancestor_depth', 0, 1, False),
                        ('check_clean_event_and', [0]),
                        ('hook', 'hook1')
                    ],
                ]
            ]
        ]]
        #
        t = A()
        t.a = 12
        #
        self.nbhook = 0
        ls = get_events_list(t)
        chk = Checker({'hook1': hook1}, self)
        sz = len(ls)
        for idx in range(sz):
            chk.check_event_and_action(idx, ls, stack)
        self.assertEqual(self.nbhook, 1, "Bad number of hook call")
        # counter example
        t = A()
        t.b = 12
        #
        self.nbhook = 0
        ls = get_events_list(t)
        chk = Checker({'hook1': hook1}, self)
        sz = len(ls)
        for idx in range(sz):
            chk.check_event_and_action(idx, ls, stack)
        self.assertEqual(self.nbhook, 0, "Bad number of hook call")

    def test_5_stack_with_attributes(self):
        class A:
            pass
        # stack for matching: A(.a=12, .b='toto')
        stack = [[
        [(0, 0), # block id, stmt id
            [
                [('value', 12), ('type', 'int'), ('capture', 'b'), ('end_node', ), ('store_ancestor_depth', 0), ('attr', 'a'), ('set_event', 0)],
                [('value', 'toto'), ('type', 'str'), ('capture', 'c'), ('end_node', ), ('store_ancestor_depth', 1), ('attr', 'b'), ('set_event', 1)],
                [
                    ('end_attrs', ),
                    ('check_attr_len', 2),
                    ('value', ),
                    ('type', 'A'),
                    ('capture', 'a'),
                    ('end_node', ),
                    ('check_ancestor_depth', 0, 1, False),
                    ('check_ancestor_depth', 1, 1, False),
                    ('check_clean_event_and', [0, 1]),
                    ('hook', 'hook1')
                ],
            ]
        ]
        ]]
        #
        t = A()
        t.a = 12
        t.b = 'toto'
        #
        self.nbhook = 0
        ls = get_events_list(t)
        chk = Checker({'hook1': hook1}, self)
        sz = len(ls)
        for idx in range(sz):
            chk.check_event_and_action(idx, ls, stack)
        self.assertEqual(self.nbhook, 1, "Bad number of hook call")
        # counter example
        #
        t = A()
        t.a = 12
        t.b = 42
        #
        self.nbhook = 0
        ls = get_events_list(t)
        chk = Checker({'hook1': hook1}, self)
        sz = len(ls)
        for idx in range(sz):
            chk.check_event_and_action(idx, ls, stack)
        self.assertEqual(self.nbhook, 0, "Bad number of hook call")

    def test_5_stack_with_capture(self):
        class B(list):
            pass
        # stack for matching: B([0: 12->b, 1: 42, 2: 'toto'])->a
        stack = [[
        [(0, 0), # block id, stmt id
            [
                [('value', 12), ('type', 'int'), ('capture', 'b'), ('end_node', ), ('store_ancestor_depth', 0), ('indice', 0), ('set_event', 0)],
                [('value', 42), ('type', 'int'), ('end_node', ), ('store_ancestor_depth', 1), ('indice', 1), ('set_event', 1)],
                [('value', 'toto'), ('type', 'str'), ('end_node', ), ('store_ancestor_depth', 2), ('indice', 2), ('set_event', 2)],
                [
                    ('end_indices', ),
                    ('check_len', 3),
                    ('value', ),
                    ('type', 'B'),
                    ('capture', 'a'),
                    ('end_node', ),
                    ('check_ancestor_depth', 0, 1, False),
                    ('check_ancestor_depth', 1, 1, False),
                    ('check_ancestor_depth', 2, 1, False),
                    ('check_clean_event_and', [0, 1, 2]),
                    ('hook', 'hook1')
                ],
            ]
        ]
        ]]
        #
        t = B([12, 42, 'toto'])
        #
        self.nbhook = 0
        ls = get_events_list(node.normalize(t))
        chk = Checker({'hook1': hook1}, self)
        sz = len(ls)
        for idx in range(sz):
            chk.check_event_and_action(idx, ls, stack)
        self.assertEqual(self.nbhook, 1, "Bad number of hook call")
        # counter example
        #
        t = B([12, 42, 'tota'])
        #
        self.nbhook = 0
        ls = get_events_list(node.normalize(t))
        chk = Checker({'hook1': hook1}, self)
        sz = len(ls)
        for idx in range(sz):
            chk.check_event_and_action(idx, ls, stack)
        self.assertEqual(self.nbhook, 0, "Bad number of hook call")

    def test_5_stack_with_dict(self):
        class C(dict):
            pass
        # stack for matching: C({'toto': 12->b, 'totu': 42, 'tutu': 'toto'})->a
        stack = [[
        [(0, 0), # block id, stmt id
            [
                [('value', 12), ('type', 'int'), ('capture', 'b'), ('end_node', ), ('store_ancestor_depth', 0), ('key', 'toto'), ('set_event', 0)],
                [('value', 42), ('type', 'int'), ('end_node', ), ('store_ancestor_depth', 1), ('key', 'totu'), ('set_event', 1)],
                [('value', 'toto'), ('type', 'str'), ('end_node', ), ('store_ancestor_depth', 2), ('key', 'tutu'), ('set_event', 2)],
                [
                    ('end_keys', ),
                    ('check_len', 3),
                    ('value', ),
                    ('type', 'C'),
                    ('capture', 'a'),
                    ('end_node', ),
                    ('check_ancestor_depth', 0, 1, False),
                    ('check_ancestor_depth', 1, 1, False),
                    ('check_ancestor_depth', 2, 1, False),
                    ('check_clean_event_and', [0, 1, 2]),
                    ('hook', 'hook1')
                ],
            ]
        ]
        ]]
        #
        t = C({'toto': 12, 'totu': 42, 'tutu': 'toto'})
        #
        self.nbhook = 0
        ls = get_events_list(node.normalize(t))
        chk = Checker({'hook1': hook1}, self)
        sz = len(ls)
        for idx in range(sz):
            chk.check_event_and_action(idx, ls, stack)
        self.assertEqual(self.nbhook, 1, "Bad number of hook call")
        # counter example
        #
        t = C({'toto': 12, 'totu': 42, 'tutu': 'tota'})
        #
        self.nbhook = 0
        ls = get_events_list(node.normalize(t))
        chk = Checker({'hook1': hook1}, self)
        sz = len(ls)
        for idx in range(sz):
            chk.check_event_and_action(idx, ls, stack)
        self.assertEqual(self.nbhook, 0, "Bad number of hook call")

    def test_5_stack_basic_with_ancestor(self):
        # stack for matching: A(...) / C(...) -> a => #hook1
        stack = [[
        [(0, 0), # block id, stmt id
            [
                [('value',), ('type', 'C'), ('capture', 'a'), ('end_node',), ('store_ancestor_depth', 0)],
                [
                    ('value', ),
                    ('type', 'A'),
                    ('end_node', ),
                    ('check_ancestor_depth', 0, 1, False),
                    ('hook', 'hook1')
                ]
            ]
        ]
        ]]
        #
        t = [1, 2, C(c=12), A(a=13), A(a=C(c=42))]
        #
        self.nbhook = 0
        ls = get_events_list(node.normalize(t))
        chk = Checker({'hook1': hook_count}, self)
        sz = len(ls)
        for idx in range(sz):
            chk.check_event_and_action(idx, ls, stack)
        self.assertEqual(self.nbhook, 1, "Bad number of hook call")

    def test_6_psl_01_type_value_attribute(self):
        class A:
            def __init__(self, **k):
                self.__dict__.update(k)
        comp_psl = PSL()
        t = {'toto':A(a=12), 'd':[1, 2, A(b=12), A(z=13), 3, A(a=12, b=A(a=12))]}
        expr = "{ A(.a=12)->a => #hook1; }"
        psl_comp = comp_psl.compile(expr)
        res = []
        match(t, psl_comp, {'hook1': test1}, res)
        self.assertEqual(len(res), 2, "Can't match: %s" % expr)

    def test_6_psl_02_type_value_wildcard(self):
        class A:
            def __init__(self, **k):
                self.__dict__.update(k)
            def __repr__(self):
                return "%s(%s)" % (type(self).__name__, ', '.join(["%s=%s" % (k, repr(v)) for k, v in vars(self).items() if k[0] != '_']))
        class B(A): pass
        class C(A): pass
        class D(A): pass
        comp_psl = PSL()
        t = {'toto':A(a=12), 'd':[1, 2, A(b=12), A(z=13), 3, B(a=A(a=D())), A(a=12, b=A(a=13))]}
        expr = "{ A(.a=*, ...)->a => #hook1; }"
        psl_comp = comp_psl.compile(expr)
        res = []
        match(t, psl_comp, {'hook1': test1}, res)
        self.assertEqual(len(res), 4, "Can't match: %s" % expr)

    def test_6_psl_03_type_attribute_wildcard(self):
        comp_psl = PSL()
        t = {'toto':A(a=12), 'd':[1, 2, A(b=12), A(z=13), 3, A(a=12, b=A(a=12))]}
        expr = "{ A(.*=12, ...)->a => #hook1; }"
        psl_comp = comp_psl.compile(expr)
        res = []
        match(t, psl_comp, {'hook1': test1}, res)
        self.assertEqual(len(res), 4, "Can't match: %s" % expr)

    def test_6_psl_04_list_all_wildcard(self):
        comp_psl = PSL()
        t = {'toto':A(a=12), 'd':[1, 2, A(b=12), A(z=13), 3, A(a=12, b=A(a=12))]}
        expr = "{ [*:* -> a, ...] => #hook1; }"
        psl_comp = comp_psl.compile(expr)
        res = []
        match(t, psl_comp, {'hook1': testlist}, res)
        self.assertEqual(len(res), 6, "Can't match: %s" % expr)

    def test_6_psl_05_list_index_wildcard(self):
        comp_psl = PSL()
        t = {'toto':A(a=12), 'd':[1, 2, A(b=12), A(z=13), 3, A(a=12, b=A(a=12))]}
        expr = "{ [*:A(...) -> a, ...] => #hook1; }"
        psl_comp = comp_psl.compile(expr)
        res = []
        match(t, psl_comp, {'hook1': testlist}, res)
        self.assertEqual(len(res), 3, "Can't match: %s" % expr)

    def test_6_psl_06_dict_all_wildcard(self):
        comp_psl = PSL()
        t = {'toto':A(a=12), 'd':{1:2, 2:3}}
        expr = "{ {*:* -> a, ...} => #hook1; }"
        psl_comp = comp_psl.compile(expr)
        res = []
        match(t, psl_comp, {'hook1': testdict}, res)
        self.assertEqual(len(res), 4, "Can't match: %s" % expr)

    def test_6_psl_07_dict_key_wildcard(self):
        comp_psl = PSL()
        t = {'toto':A(a=12), 'd':{1:A(), 2:A(a=3), 3:A(b=12, a=13), 4:A(b=13, a=12)}}
        expr = "{ {*:A(.a=12, ...) -> a, ...} => #hook1; }"
        psl_comp = comp_psl.compile(expr)
        res = []
        match(t, psl_comp, {'hook1': testdict}, res)
        self.assertEqual(len(res), 2, "Can't match: %s" % expr)

    def test_6_psl_08_ancestor_simple(self):
        comp_psl = PSL()
        t = A(l=[B(c=C(n=12)), C(b=B()), D(c=C(n=21)), B(a=A(c=C(n=13))), B(a=A(d=D(c=C(n=31))))])
        expr = "{ B(...) -> b / C(...) -> c => #hook1; }"
        psl_comp = comp_psl.compile(expr)
        res = []
        match(t, psl_comp, {'hook1': testcopy}, res)
        self.assertEqual(len(res), 1, "Only one capture with depth exactly 1: %s" % repr(res))
        self.assertEqual(res[0]['c'].n, 12, "the C with 12 as value")

    def test_6_psl_09_ancestor_depth_variable(self):
        comp_psl = PSL()
        t = A(l=[B(c=C(n=12)), C(b=B()), D(c=C(n=21)), B(a=A(c=C(n=13))), B(a=A(d=D(c=C(n=31))))])
        expr = "{ B(...) -> b /+ C(...) -> c => #hook1; }"
        psl_comp = comp_psl.compile(expr)
        res = []
        match(t, psl_comp, {'hook1': testcopy}, res)
        self.assertEqual(len(res), 3, "Only 3 capture with depth minimun 1: %s" % repr(res))
        self.assertEqual(res[1]['c'].n, 13, "the 2nd C with 13 as value")

    def test_6_psl_10_ancestor_depth_fix(self):
        comp_psl = PSL()
        t = A(l=[B(c=C(n=12)), C(b=B()), D(c=C(n=21)), B(a=A(c=C(n=13))), B(a=A(d=D(c=C(n=31))))])
        expr = "{ B(...) -> b /3 C(...) -> c => #hook1; }"
        psl_comp = comp_psl.compile(expr)
        res = []
        match(t, psl_comp, {'hook1': testcopy}, res)
        self.assertEqual(len(res), 1, "Only one capture with 3 depth: %s" % repr(res))
        self.assertEqual(res[0]['c'].n, 31, "the C with 31 as value")

    def test_6_psl_11_sibling(self):
        comp_psl = PSL()
        ## we don't care of order, we match a list of same depth patterns
        t = A(l=[B(c=C(n=12)), C(b=B()), D(c=C(n=21)), B(a=A(c=C(n=13))), C(), B(a=A(d=D(c=C(n=31)))), A(), C(), D()])
        expr = "{ B(...) -> b ~~ C(...) -> c ~~ D(...) -> d => #hook1;}"
        psl_comp = comp_psl.compile(expr)
        res = []
        match(t, psl_comp, {'hook1': testcopy}, res)
        self.assertEqual(len(res), 1, "Can't match sibling: %s" % repr(res))
        self.assertIn('b', res[0], "Can't capture 'b'")
        self.assertIn('c', res[0], "Can't capture 'c'")
        self.assertIn('d', res[0], "Can't capture 'd'")

    def test_6_psl_12_event_precond(self):
        comp_psl = PSL()
        t = A(l=[B(), C(), D()])
        expr = """
            {
                C(...) -> c && (Event) => #hook;
                B(...) => Event;
            }
        """
        psl_comp = comp_psl.compile(expr)
        res = []
        match(t, psl_comp, {'hook': testcopy}, res)
        self.assertEqual(len(res), 1, "Can't mach with event")
        self.assertIs(type(res[0]['c']), C, "Can't mach with event")

    def test_6_psl_13_event_and(self):
        comp_psl = PSL()
        t = A(l=[B(), C(), D(a=12), A(), D(a=42)])
        expr = """
            {
                A(...) => E1;
                B(...) => E2;
                C(...) => E3;
                D(...) -> d && (E1 & E2 & E3) => #hook;
            }
        """
        psl_comp = comp_psl.compile(expr)
        res = []
        match(t, psl_comp, {'hook': testcopy}, res)
        self.assertEqual(len(res), 1, "Can't mach with event")
        self.assertIs(type(res[0]['d']), D, "Can't mach with event")
        self.assertEqual(res[0]['d'].a, 42, "Can't mach with event")

    def test_6_psl_14_event_or(self):
        comp_psl = PSL()
        t = A(l=[B(), C(), D(a=12), A(), D(a=42)])
        expr = """
            {
                A(...) => E1;
                B(...) => E2;
                C(...) => E3;
                D(...) -> d && (E1 | E2 | E3) => #hook;
            }
        """
        psl_comp = comp_psl.compile(expr)
        res = []
        match(t, psl_comp, {'hook': testcopy}, res)
        self.assertEqual(len(res), 2, "Can't mach with event")
        self.assertIs(type(res[0]['d']), D, "Can't mach with event")
        self.assertEqual(res[0]['d'].a, 12, "Can't mach with event")
        self.assertIs(type(res[1]['d']), D, "Can't mach with event")
        self.assertEqual(res[1]['d'].a, 42, "Can't mach with event")

    def test_6_psl_15_event_xor(self):
        comp_psl = PSL()
        t = A(l=[B(), C(), D(a=12), A(), D(a=42), B(), D(a=14), B(), A(), D(a=66)])
        expr = """
            {
                A(...) => E1;
                B(...) => E2;
                C(...) && (E1 | E2) => E3;
                D(...) -> d && (E1 ^ E2) => #hook;
            }
        """
        psl_comp = comp_psl.compile(expr)
        res = []
        match(t, psl_comp, {'hook': testcopy}, res)
        self.assertEqual(len(res), 2, "Can't mach with event: %s" % res)
        self.assertIs(type(res[0]['d']), D, "Can't mach with event")
        self.assertEqual(res[0]['d'].a, 42, "Can't mach with event")

    def test_6_psl_16_event_not(self):
        def is_called(capture, user_data):
            user_data.call += 1
            if not hasattr(user_data, 'b'):
                user_data.b = [capture['b']]
            else:
                user_data.b.append(capture['b'])
        comp_psl = PSL()
        t = C(l=[B(b=1), A(), B(b=2), B(b=3)])
        expr = """
            {
                A(...) => E1;
                B(...) -> b && (!E1) => #hook;
                B(...) && (E1 & E1) => null;
            }
        """
        psl_comp = comp_psl.compile(expr)
        ud = A()
        ud.call = 0
        print("!!! NOT: %s" % repr(psl_comp.stack))
        match(t, psl_comp, {'hook': is_called}, ud)
        print("!!!")
        #self.assertEqual(ud.call, 2, "Can't manage Not: %s" % repr(ud))

    def test_6_psl_17_iskindof(self):
        comp_psl = PSL()
        t = [1, 2, B(a=12), A(), A(z=C(a=12))]
        comp_psl = PSL()
        expr = "{ A?(...)->a => #hook1; }"
        psl_comp = comp_psl.compile(expr)
        res = []
        match(t, psl_comp, {'hook1': testcopy}, res)
        self.assertEqual(len(res), 4, "We must fail: %s" % repr(res))

    def test_6_psl_bugfix_1_ancestor_are_related(self):
        comp_psl = PSL()
        t = A(l=[A(c=C(n=12)), B(z=44), D(c=C(n=21)), B(a=A(c=C(n=13))), B(a=A(d=D(c=C(n=31))))])
        expr = "{ B(...) -> b / C(...) -> c => #hook1; }"
        psl_comp = comp_psl.compile(expr)
        res = []
        match(t, psl_comp, {'hook1': testcopy}, res)
        self.assertFalse(len(res) == 1, "No capture of not related ancestors")

    def test_6_psl_bugfix_2_attribute_related_to_direct_ancestor(self):
        comp_psl = PSL()
        t = [1, 2, B(a=12), A(), A(z=C(a=12))]
        comp_psl = PSL()
        expr = "{ A(.a=12)->a => #hook1; }"
        psl_comp = comp_psl.compile(expr)
        res = []
        match(t, psl_comp, {'hook1': test1}, res)
        self.assertFalse(len(res) == 1, "We must fail: %s" % repr(res))
