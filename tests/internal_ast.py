import unittest

import pdb

# TODO: move in ast
from pyrser.parsing.node import *
from pyrser.passes.to_yml import *

from pyrser.ast.state import *
from pyrser.ast.walk import *
from pyrser.ast.match import *

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


    def test_000(self):
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
        self.assertEqual(str(lbegin.thelist()), "['a', 'b', 'd', 'e', 'f']", "Bad construction of l")
        self.assertEqual(l.thelist().must_update, True, "Bad construction of l")
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


    def test_00(self):
        """Basic test on state creation"""
        nsr = StateRegister()
        s0 = State(nsr)
        s1 = State(nsr)
        self.assertIn(s0, nsr, "Failed State %d in StateRegister" % id(s0))
        self.assertIn(s1, nsr, "Failed State %d in StateRegister" % id(s1))
        # attr, indice, key, value, type, default
        s0.matchAttr('a', s1)
        self.assertEqual(id(s1), id(s0.checkAttr('a')), "Failed to return correct state")
        s0.matchIndice(1, s1)
        self.assertEqual(id(s1), id(s0.checkIndice(1)), "Failed to return correct state")
        s0.matchKey('tutu', s1)
        self.assertEqual(id(s1), id(s0.checkKey('tutu')), "Failed to return correct state")
        s0.matchValue('tutu', s1)
        self.assertEqual(id(s1), id(s0.checkValue('tutu')), "Failed to return correct state")
        s0.matchType(int, s1)
        self.assertEqual(id(s1), id(s0.checkType(int)), "Failed to return correct state")
        s0.matchDefault(s1)
        self.assertEqual(id(s1), id(s0.doDefault()), "Failed to return correct state")
        #   Event
        s0.matchEvent('lolo', s1)
        self.assertEqual(id(s1), id(s0.doResultEvent()), "Failed to return correct state")
        #   Hook
        def dummy(nodes, user_data):
            pass
        s0.matchHook(dummy, s1)
        sh = s0.default_hook
        self.assertTrue(type(sh) is StateHook, "Failed to return correct state")
        self.assertEqual(id(s1), id(s0.doResultHook()), "Failed to return correct state")

    def test_01(self):
        """Event Expr event"""
        nsr = StateRegister()
        s0 = State(nsr)
        s1 = State(nsr)
        s2 = State(nsr)
        # set one event
        s1.matchEvent('lolo', s0)
        self.assertIn('lolo', nsr.named_events, "Failed to set an event")
        sX = s1.doResultEvent()
        self.assertEqual(id(s0), id(sX), "Failed to init the event for the test")
        # check if is set
        e = EventNamed('lolo')
        s2 = State(nsr)
        s0.matchEventExpr(e, s2, False)
        self.assertEqual(id(s2), id(s0.checkEventExpr()), "Failed to return correct state")
        # ?? ( ... )  is the syntax for none cleaning event expression
        #?? ( lala & lulu )
        s0.cleanAll()
        s3 = State(nsr)
        s3.matchEvent('lala', s0)
        s3.doResultEvent()
        e = EventSeq([EventNamed('lala'), EventNamed('lulu')])
        s0.matchEventExpr(e, s2, False)
        sX = s0.checkEventExpr()
        self.assertTrue(id(s2) != id(sX), "Failed to return correct state")
        s4 = State(nsr)
        s4.matchEvent('lulu', s0)
        s4.doResultEvent()
        self.assertTrue(id(s2) == id(s0.checkEventExpr()), "Failed to return correct state")
        #?? ( lala & !lulu )
        s0.events_expr = list()
        s0.cleanAll()
        s3.matchEvent('lala', s0)
        s3.doResultEvent()
        s4.matchEvent('lulu', s0)
        s4.doResultEvent()
        e = EventSeq([EventNamed('lala'), EventNot(EventNamed('lulu'))])
        s0.matchEventExpr(e, s2, False)
        sX = s0.checkEventExpr()
        self.assertTrue(id(s2) != id(sX), "Failed to return correct state")
        s0.cleanAll()
        s3.matchEvent('lala', s0)
        s3.doResultEvent()
        sX = s0.checkEventExpr()
        self.assertTrue(id(s2) == id(sX), "Failed to return correct state")
        #?? ( lala | lulu )
        s0.events_expr = list()
        s0.cleanAll()
        s4.matchEvent('lulu', s0)
        s4.doResultEvent()
        e = EventAlt([EventNamed('lala'), EventNamed('lulu')])
        s0.matchEventExpr(e, s2, False)
        sX = s0.checkEventExpr()
        self.assertTrue(id(s2) == id(sX), "Failed to return correct state")
        #?? ( lala & ( lolo | lulu) )
        s0.events_expr = list()
        nsr.cleanAll()
        s3.matchEvent('lala', s0)
        s3.doResultEvent()
        s4.matchEvent('lulu', s0)
        s4.doResultEvent()
        e = EventSeq([EventNamed('lala'), EventAlt([EventNamed('lolo'), EventNamed('lulu')])])
        s0.matchEventExpr(e, s2, False)
        sX = s0.checkEventExpr()
        self.assertTrue(id(s2) == id(sX), "Failed to return correct state")
        #? ( lala & lulu )
        s0.events_expr = list()
        s0.cleanAll()
        s3 = State(nsr)
        s3.matchEvent('lala', s0)
        s3.doResultEvent()
        s4.matchEvent('lulu', s0)
        s4.doResultEvent()
        e = EventSeq([EventNamed('lala'), EventNamed('lulu')])
        s0.matchEventExpr(e, s2, True)
        sX = s0.checkEventExpr()
        self.assertTrue(id(s2) == id(sX), "Failed to return correct state")
        self.assertFalse('lala' in nsr.named_events, "Events not correctly clean after match")
        self.assertFalse('lulu' in nsr.named_events, "Events not correctly clean after match")
        #? (lala & ( lolo | lulu))
        s0.events_expr = list()
        nsr.cleanAll()
        s3.matchEvent('lala', s0)
        s3.doResultEvent()
        s4.matchEvent('lulu', s0)
        s4.doResultEvent()
        s5 = State(nsr)
        s5.matchEvent('lolo', s0)
        s5.doResultEvent()
        e = EventSeq([EventNamed('lala'), EventAlt([EventNamed('lolo'), EventNamed('lulu')])])
        s0.matchEventExpr(e, s2, True)
        sX = s0.checkEventExpr()
        self.assertTrue(id(s2) == id(sX), "Failed to return correct state")
        self.assertFalse('lala' in nsr.named_events, "Events not correctly clean after match")
        self.assertFalse('lolo' in nsr.named_events, "Events not correctly clean after match")
        self.assertFalse('lulu' in nsr.named_events, "Events not correctly clean after match")

    def test_03(self):
        """Test tree automata construction"""
        def checkMatch(tree: Node, user_data) -> Node:
            pass
        # { Test(.b = 42) -> #checkMatch; Test(.c = 42) -> #checkMatch; }
        m = MatchBlock([
            MatchHook(checkMatch, MatchType(Test, [MatchAttr('b', MatchValue(42))])),
            MatchHook(checkMatch, MatchType(Test, [MatchAttr('c', MatchValue(42))])),
        ])
        tree = list()
        nsr = StateRegister()
        m.build_state_tree(tree, nsr)
        nsr.label = repr(m)
        nsr.to_png_file(rpath + os.sep + 't3_1.png')
        self.assertEqual(len(m.root_edge.next_edge), 1, "1 edge expected at this state for this pattern")
        it = iter(m.root_edge.next_edge.values())
        eX = next(it)
        self.assertEqual(len(eX.next_edge), 2, "2 edge expected at this state for this pattern")
        # { Test(.b = 42) -> #checkMatch; A(.b = 42) -> #checkMatch; }
        class A: pass
        m = MatchBlock([
            MatchHook(checkMatch, MatchType(Test, [MatchAttr('b', MatchValue(42))])),
            MatchHook(checkMatch, MatchType(A, [MatchAttr('b', MatchValue(42))])),
        ])
        tree = list()
        nsr = StateRegister()
        m.build_state_tree(tree, nsr)
        nsr.label = repr(m)
        nsr.to_png_file(rpath + os.sep + 't3_2.png')
        self.assertEqual(len(m.root_edge.next_edge), 1, "1 edge expected at this state for this pattern")
        it = iter(m.root_edge.next_edge.values())
        eX = next(it)
        self.assertEqual(len(eX.next_edge), 1, "1 edge expected at this state for this pattern")
        it = iter(eX.next_edge.values())
        eX = next(it)
        self.assertEqual(len(eX.next_edge), 2, "2 edge expected at this state for this pattern")

    def test_04(self):
        """Test tree automata construction"""
        def checkMatch(tree: Node, user_data) -> Node:
            pass
        def otherHook(tree: Node, user_data) -> Node:
            pass
        lc = LivingContext()
        # { Test(.b = 42) -> #checkMatch; }
        m = MatchBlock([
            MatchHook(checkMatch, MatchType(Test, [MatchAttr('b', MatchValue(42))])),
        ])
        lc.add_match_block(m)
        # { Test(.b = 42) -> #otherHook; }
        m = MatchBlock([
            MatchHook(otherHook, MatchType(Test, [MatchAttr('b', MatchValue(42))])),
        ])
        lc.add_match_block(m)
        lc.build_automata()
        lc.to_png_file(rpath + os.sep + 't4_1.png')

    def test_05(self):
        """basic tree matching"""
        def checkMatch1(tree: Node, user_data) -> Node:
            global in_test
            in_test = True
            user_data[1].assertEqual(user_data[0], id(tree.node()), "Failed to match the node of tree")
            user_data[1].assertEqual(tree.attrs[0].value, 'b', "Failed to match the node of tree")
            user_data[1].assertEqual(tree.attrs[0].get(), 42, "Failed to match the node of tree")
        def checkMatch2(tree: Node, user_data) -> Node:
            global in_test
            in_test = True
            user_data[1].assertEqual(user_data[0], id(tree.node()), "Failed to match the node of tree")
            user_data[1].assertEqual(tree.attrs[0].value, 'a', "Failed to match the node of tree")
            user_data[1].assertEqual(tree.attrs[0].get(), 42, "Failed to match the node of tree")
            user_data[1].assertEqual(tree.attrs[1].value, 'c', "Failed to match the node of tree")
            user_data[1].assertEqual(tree.attrs[1].get(), 1.2, "Failed to match the node of tree")
        def checkMatch3(tree: Node, user_data) -> Node:
            global in_test
            in_test = True
            user_data[1].assertEqual(user_data[0], id(tree.node()), "Failed to match the node of tree")
            user_data[1].assertEqual(tree.indices[0].value, 2, "Failed to match the node of tree")
            user_data[1].assertEqual(tree.indices[0].get(), 42, "Failed to match the node of tree")
        def checkMatch4(tree: Node, user_data) -> Node:
            global in_test
            in_test = True
            user_data[1].assertEqual(user_data[0], id(tree.node()), "Failed to match the node of tree")
            user_data[1].assertEqual(tree.keys[0].value, 'toto', "Failed to match the node of tree")
            user_data[1].assertEqual(tree.keys[0].get(), 42, "Failed to match the node of tree")
        def checkMatch5(tree: Node, user_data) -> Node:
            global in_test
            print("MATCH TREE %s" % repr(tree.attrs), flush=True)
            in_test = True
            user_data[1].assertEqual(user_data[0], id(tree.node()), "Failed to match the node of tree")
            user_data[1].assertEqual(tree.attrs[0].value, 'a', "Failed to match the node of tree")
            user_data[1].assertEqual(tree.attrs[0].get(), 12, "Failed to match the node of tree")
            user_data[1].assertEqual(tree.attrs[1].value, 'c', "Failed to match the node of tree")
            user_data[1].assertEqual(tree.attrs[1].get(), 42, "Failed to match the node of tree")
        def checkMatch(tree: Node, user_data) -> Node:
            global in_test
            in_test = True
            user_data[1].assertEqual(user_data[0], id(tree.node()), "Failed to match the node of tree")
        def checkNoMatch(tree: Node, user_data) -> Node:
            global in_test
            in_test = True

        global in_test
        # Test(.b = 42) -> #checkMatch1;
        m = MatchBlock([
            MatchHook(checkMatch1, MatchType(Test, [MatchAttr('b', MatchValue(42))])),
        ])
        lc = LivingContext()
        lc.add_match_block(m)
        lc.build_automata()
        lc.to_png_file(rpath + os.sep + 't5_1.png')
        t = [Test()]
        t[0].b = 42
        t.append(A())
        t[1].b = 42
        in_test = False
        walk(t, lc, (id(t[0]), self))
        self.assertTrue(in_test, "Expect the Hook checkMatch is called")
        #self.assertTrue(lc.is_in_stable_state(), "LivingContext not in correct state")
        # Test(.b = 42) -> #checkNoMatch;
        m = MatchBlock([
            MatchHook(checkNoMatch, MatchType(Test, [MatchAttr('b', MatchValue(42))])),
        ])
        lc = LivingContext()
        lc.add_match_block(m)
        lc.build_automata()
        lc.to_png_file(rpath + os.sep + 't5_2.png')
        t = Test()
        t.a = 42
        t.b = 12
        in_test = False
        walk(t, lc, (id(t), self))
        self.assertFalse(in_test, "Expect that the Hook checkNoMatch isn't called")
        #self.assertTrue(lc.is_in_stable_state(), "LivingContext not in correct state")
        # Test(.a=42, .c=1.2) -> #checkMatch2;
        m = MatchBlock([
            MatchHook(checkMatch2, MatchType(Test, [MatchAttr('a', MatchValue(42)), MatchAttr('c', MatchValue(1.2))])),
        ])
        c = LivingContext()
        lc.add_match_block(m)
        lc.build_automata()
        lc.to_png_file(rpath + os.sep + 't5_3.png')
        t = Test()
        t.a = 42
        t.c = 1.2
        in_test = False
        walk(t, lc, (id(t), self))
        self.assertTrue(in_test, "Expect that the Hook checkMatch is called")
        #self.assertTrue(lc.is_in_stable_state(), "LivingContext not in correct state")
        t = Test()
        t.a = 42
        t.b = Test()
        t.b.c = 1.2
        in_test = False
        walk(t, lc, (id(t), self))
        self.assertFalse(in_test, "Expect that the Hook checkMatch isn't called")
        #self.assertTrue(lc.is_in_stable_state(), "LivingContext not in correct state")
        # L([2: 42]) -> #checkMatch3;
        m = MatchBlock([
            MatchHook(checkMatch3, MatchType(L, [MatchIndice(2, MatchValue(42))])),
        ])
        lc = LivingContext()
        lc.add_match_block(m)
        lc.build_automata()
        lc.to_png_file(rpath + os.sep + 't5_4.png')
        t = [L(), L(), L()]
        t[0].append(10)
        t[0].append(42)
        t[1].append(11)
        t[1].append(12)
        t[1].append(13)
        t[2].append(14)
        t[2].append(15)
        t[2].append(42)
        in_test = False
        walk(t, lc, (id(t[2]), self))
        self.assertTrue(in_test, "Expect the Hook checkMatch is called")
        #self.assertTrue(lc.is_in_stable_state(), "LivingContext not in correct state")
        # H({'toto': 42}) -> #checkMatch4;
        m = MatchBlock([
            MatchHook(checkMatch4, MatchType(H, [MatchKey('toto', MatchValue(42))])),
        ])
        lc = LivingContext()
        lc.add_match_block(m)
        lc.build_automata()
        lc.to_png_file(rpath + os.sep + 't5_5.png')
        t = [H(), H(), H()]
        t[0]['chausette'] = 12
        t[0]['toto'] = 12
        t[1]['toto'] = 42
        t[2]['zozo'] = 42
        in_test = False
        walk(t, lc, (id(t[1]), self))
        self.assertTrue(in_test, "Expect the Hook checkMatch is called")
        #self.assertTrue(lc.is_in_stable_state(), "LivingContext not in correct state")
        # Test(.a = 12, .c = 42, ...) -> #checkMatch5;
        m = MatchBlock([
            MatchHook(checkMatch5, MatchType(Test, [MatchAttr('a', MatchValue(12)), MatchAttr('c', MatchValue(42))], strict=False)),
        ])
        lc = LivingContext()
        lc.add_match_block(m)
        lc.build_automata()
        lc.to_png_file(rpath + os.sep + 't5_6.png')
        t = [Test(), Test()]
        t[0].a = 12
        t[0].b = 42
        t[1].a = 12
        t[1].b = 22
        t[1].c = 42
        t = normalize(t)
        in_test = False
        print("WALK BEGIN")
        pdb.set_trace()
        walk(t, lc, (id(t[1]), self))
        self.assertTrue(in_test, "Expect the Hook checkMatch is called")
        #self.assertTrue(lc.is_in_stable_state(), "LivingContext not in correct state")
        # Test^(.b = 42) -> #checkMatch;
        class ChildTest(Test): pass
        m = MatchBlock([
            MatchHook(checkMatch, MatchType(Test, [MatchAttr('b', MatchValue(42))], iskindof=True)),
        ])
        lc = LivingContext()
        lc.add_match_block(m)
        lc.build_automata()
        lc.to_png_file(rpath + os.sep + 't5_7.png')
        t = [ChildTest()]
        t[0].b = 42
        t.append(A())
        t[1].b = 42
        in_test = False
        walk(t, lc, (id(t[0]), self))
        self.assertTrue(in_test, "Expect the Hook checkMatch is called")
        #self.assertTrue(lc.is_in_stable_state(), "LivingContext not in correct state")

    def test_06(self):
        """tree rewriting"""
        def checkMatch1(tree: Node, user_data):
            global in_test
            in_test = True
            user_data[1].assertEqual(user_data[0], id(tree.node()), "Failed to match the node of tree")
            idx = tree.parent.index(tree.node())
            tree.parent[idx] = "rewrited"
        def checkMatch2(tree: Node, user_data):
            global in_test
            in_test = True
            user_data[1].assertEqual(user_data[0], id(tree.node()), "Failed to match the node of tree")
            idx = tree.parent.index(tree.node())
            tree.parent[idx] = "rewrited"
        def checkMatch3(tree: Node, user_data):
            global in_test
            in_test = True
            user_data[1].assertEqual(user_data[0], id(tree.node()), "Failed to match the node of tree")
            idx = tree.parent.index(tree.node())
            tree.parent[idx] = "rewrited"
        def checkMatch4(tree: Node, user_data):
            global in_test
            in_test = True
            idx = tree.parent.index(tree.node())
            tree.parent[idx] = "rewrited"
        global in_test
        # Test(.b = 42) -> #checkMatch1;
        m = MatchBlock([
            MatchHook(checkMatch1, MatchType(Test, [MatchAttr('b', MatchValue(42))])),
        ])
        lc = LivingContext()
        lc.add_match_block(m)
        lc.build_automata()
        lc.to_png_file(rpath + os.sep + 't6_1.png')
        t = [Test()]
        t[0].b = 42
        t.append(A())
        t[1].b = 42
        in_test = False
        walk(t, lc, (id(t[0]), self))
        self.assertTrue(in_test, "Expect the Hook checkMatch is called")
        #self.assertTrue(lc.is_in_stable_state(), "LivingContext not in correct state")
        self.assertEqual(t[0], "rewrited", "Failed to rewrite a node")
        # L([2: 42]) -> #checkMatch2;
        m = MatchBlock([
            MatchHook(checkMatch2, MatchType(L, [MatchIndice(2, MatchValue(42))])),
        ])
        lc = LivingContext()
        lc.add_match_block(m)
        lc.build_automata()
        lc.to_png_file(rpath + os.sep + 't6_2.png')
        t = [L(), L(), L()]
        t[0].append(10)
        t[0].append(42)
        t[1].append(11)
        t[1].append(12)
        t[1].append(13)
        t[2].append(14)
        t[2].append(15)
        t[2].append(42)
        in_test = False
        walk(t, lc, (id(t[2]), self))
        self.assertTrue(in_test, "Expect the Hook checkMatch is called")
        #self.assertTrue(lc.is_in_stable_state(), "LivingContext not in correct state")
        self.assertEqual(t[2], "rewrited", "Failed to rewrite a node")
        # H({'toto': 42}) -> #checkMatch3;
        m = MatchBlock([
            MatchHook(checkMatch3, MatchType(H, [MatchKey('toto', MatchValue(42))])),
        ])
        lc = LivingContext()
        lc.add_match_block(m)
        lc.build_automata()
        lc.to_png_file(rpath + os.sep + 't6_3.png')
        t = ListNode([H(), H(), H()])
        t[0]['chausette'] = 12
        t[0]['toto'] = 13
        t[1]['toto'] = 42
        t[2]['zozo'] = 43
        print("HHHHHHHHH %s" % repr(t))
        in_test = False
        walk(t, lc, (id(t[1]), self)) ###
        self.assertTrue(in_test, "Expect the Hook checkMatch is called")
        #self.assertTrue(lc.is_in_stable_state(), "LivingContext not in correct state")
        self.assertEqual(t[1], "rewrited", "Failed to rewrite a node")
        # Test(.a = 12, .c = 42, ...) -> #checkMatch4;
        m = MatchBlock([
            MatchHook(checkMatch4, MatchType(Test, [MatchAttr('a', MatchValue(12)), MatchAttr('c', MatchValue(42))], strict=False)),
        ])
        lc = LivingContext()
        lc.add_match_block(m)
        lc.build_automata()
        lc.to_png_file(rpath + os.sep + 't6_4.png')
        t = ListNode([Test(), Test(), Test(), Test(), Test()])
        t[0].a = 12
        t[0].b = 42
        t[1].a = 12
        t[1].b = 22
        t[1].c = 42
        t[2] = "glubu"
        t[3].c = 42
        t[3].a = 12
        t[3].g = "plop"
        in_test = False
        walk(t, lc)
        self.assertTrue(in_test, "Expect the Hook checkMatch is called")
        #self.assertTrue(lc.is_in_stable_state(), "LivingContext not in correct state")
        self.assertEqual(t[1], "rewrited", "Failed to rewrite a node")
        self.assertEqual(t[3], "rewrited", "Failed to rewrite a node")

    def test_07(self):
        """wildcard tree matching"""
        global in_test
        # Test(.b = *) -> #checkMatch;
        def checkMatch1(tree: Node, user_data):
            global in_test
            in_test = True
            tree.node().is_rewrited = True
        m = MatchBlock([
            MatchHook(checkMatch1, MatchType(Test, [MatchAttr('b')])),
        ])
        lc = LivingContext()
        lc.add_match_block(m)
        lc.build_automata()
        lc.to_png_file(rpath + os.sep + 't7_1.png')
        t = [Test()]
        t[0].b = 42
        t.append(A())
        t[1].b = 666
        t.append(Test())
        t[2].b = "cool"
        in_test = False
        walk(t, lc)
        self.assertTrue(in_test, "Expect the Hook checkMatch is called")
        self.assertTrue(hasattr(t[0], "is_rewrited"), "Failed to rewrite a node")
        self.assertTrue(hasattr(t[2], "is_rewrited"), "Failed to rewrite a node")
        #self.assertFalse(lc.is_in_stable_state(), "LivingContext not in correct state due to WILDCAR MATCH")
        # L([2: *]) -> #checkMatch2;
        def checkMatch2(tree: Node, user_data):
            global in_test
            in_test = True
            print("++++++++++")
            tree.get().is_rewrited = True
            print("==========")
            print("RECV %s" % tree.dbg_str())
        m = MatchBlock([
            MatchHook(checkMatch2, MatchType(L, [MatchIndice(2)])),
        ])
        lc = LivingContext()
        lc.add_match_block(m)
        lc.build_automata()
        lc.to_png_file(rpath + os.sep + 't7_2.png')
        t = L()
        t.append(Test())
        t.append(A())
        t.append(L())
        t[0].a = 42
        t[1].b = 42
        t[2].c = 42
        t[2].subls = [0, 1, L([2, 3, Test(), 4]), 5]
        t = normalize(t)
        in_test = False
        with self.assertRaises(ValueError):
            walk(t, lc)
        t[2].subls = L([0, 1, L([2, 3, Test(), 4]), 5])
        walk(t, lc)
        self.assertTrue(in_test, "Expect the Hook checkMatch is called")
        self.assertTrue(hasattr(t[2], "is_rewrited"), "Failed to rewrite a node")
        self.assertTrue(hasattr(t[2].subls[2][2], "is_rewrited"), "Failed to rewrite a node")
        #self.assertFalse(lc.is_in_stable_state(), "LivingContext not in correct state due to WILDCAR MATCH")
        # H({'toto': *}) -> #checkMatch;
        def checkMatch3(tree: Node, user_data):
            global in_test
            in_test = True
            tree.node().is_rewrited = True
        m = MatchBlock([
            MatchHook(checkMatch3, MatchType(H, [MatchKey("toto")])),
        ])
        lc = LivingContext()
        lc.add_match_block(m)
        lc.build_automata()
        lc.to_png_file(rpath + os.sep + 't7_3.png')
        t = H()
        t['bla'] = Test()
        t['bla'].a = 42
        t['toto'] = Test()
        t['toto'].b = 42
        t['blu'] = Test()
        t['blu'].c = 42
        t['blu'].subh = {'t': 0, 'x': 1, 'toto': H({'2': 2, '3': 3, 'toto': Test(), '4': 4}), 'z': 5}
        in_test = False
        with self.assertRaises(ValueError):
            walk(t, lc)
        t['blu'].subh = H({'t': 0, 'x': 1, 'toto': H({'2': 2, '3': 3, 'toto': Test(), '4': 4}), 'z': 5})
        walk(t, lc)
        self.assertTrue(in_test, "Expect the Hook checkMatch is called")
        self.assertTrue(hasattr(t, "is_rewrited"), "Failed to rewrite a node")
        self.assertTrue(hasattr(t['blu'].subh['toto'], "is_rewrited"), "Failed to rewrite a node")
        #self.assertFalse(lc.is_in_stable_state(), "LivingContext not in correct state due to WILDCAR MATCH")
        # Test([*: 12]) -> #checkMatch;
        print('-------------------------------------------------------------------------------')
        def checkMatch4(tree: Node, user_data):
            global in_test
            in_test = True
            tree.node().is_rewrited = True
        m = MatchBlock([
            MatchHook(checkMatch4, MatchType(L, [MatchIndice(None, MatchValue(12))])),
        ])
        lc = LivingContext()
        lc.add_match_block(m)
        lc.build_automata()
        lc.to_png_file(rpath + os.sep + 't7_4.png')
        t = L([1, 12, 2, 12, 3, 12])
        in_test = False
        walk(t, lc)
        self.assertTrue(in_test, "Expect the Hook checkMatch is called")
        self.assertTrue(hasattr(t, "is_rewrited"), "Failed to rewrite a node")
        # Test(.* = *) -> #checkMatch;
        # *(.a = 12) -> #checkMatch;
        # L([*: 12]) -> #checkMatch;
        # L([*: *]) -> #checkMatch;
        # H({*: 12}) -> #checkMatch;
        # H({*: *}) -> #checkMatch;

    def test_08(self):
        """CollectContext test for tree matching"""
        class A(Node): pass
        a = A()
        a.attr1 = 6.6
        a["toto"] = 42
        a["plop"] = 'gram'
        ##
        ct = CaptureContext()
        ct.is_key(a, "toto")
        ct2 = CaptureContext()
        ct2.is_key(a, "plop")
        ctx = CaptureContext.make_from_unorder_list([ct, ct2])
        ctx.is_node(a, "A")
        ca = CaptureContext().is_attr(a, "attr1")
        ctx.add_sub(ca)
        self.assertEqual(a.attr1, ca.get(), "Failed to get a captured value in a tree")
        self.assertEqual(a["toto"], ct.get(), "Failed to get a captured value in a tree")
        self.assertEqual(a["plop"], ct2.get(), "Failed to get a captured value in a tree")
        ct.set('pouet')
        ct2.set('chaussure')
        ca.set(999)
        self.assertEqual(a.attr1, 999, "Failed to get a captured value in a tree")
        self.assertEqual(a["toto"], "pouet", "Failed to get a captured value in a tree")
        self.assertEqual(a["plop"], "chaussure", "Failed to get a captured value in a tree")
        ctx.set(Node())
        self.assertTrue(not hasattr(ctx, 'keys'), "Failed to clean a node by setting it")


    def test_09(self):
        """node.normalize test"""
        # dict
        d = {'blabal': 12, 'lolo': 555, 'hyhy': 1000}
        d = normalize(d)
        self.assertTrue(type(d) is DictNode)
        d = {'blabal': 12, 'hash':{'xoxo': 111, 'koko': 44, 'juju': 12121}, 'lolo': 555, 'hyhy': 1000}
        d = normalize(d)
        self.assertTrue(type(d) is DictNode)
        self.assertTrue(type(d['hash']) is DictNode)
        # list
        l = L()
        l.append(12)
        l.append(23)
        l.append([1, 3, 4, 5])
        l.append(45)
        l = normalize(l)
        self.assertTrue(type(l) is L)
        self.assertTrue(type(l[2]) is ListNode)
        # tuple
        t = (1, 2, 3)
        t = normalize(t)
        self.assertTrue(type(t) is TupleNode)
        t = (1, [2, {'toto': 5}], 3)
        t = normalize(t)
        self.assertTrue(type(t) is TupleNode)
        self.assertTrue(type(t[1]) is ListNode)
        self.assertTrue(type(t[1][1]) is DictNode)
        r = weakref.ref(t[1][1])
        r()['glagla'] = 'chaussette'
        self.assertIn('glagla', t[1][1])
        self.assertEqual(t[1][1]['glagla'], 'chaussette')
        l = [1, 2, [3, 4, [5, 6], 7], 8]
        l = normalize(l)
        r = weakref.ref(l[2][2])
        r()[1] = 42
        self.assertEqual(l[2][2][1], 42)


