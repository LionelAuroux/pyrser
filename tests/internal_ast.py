import unittest

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


class InternalAst_Test(unittest.TestCase):
    def test_00(self):
        """Basic test on state creation"""
        nsr = StateRegister()
        s0 = State(nsr)
        s1 = State(nsr)
        self.assertIn(s0, nsr, "Failed State %d in StateRegister" % id(s0))
        self.assertIn(s1, nsr, "Failed State %d in StateRegister" % id(s1))
        # attr, indice, key, value, type, default
        s0.matchAttr('a', s1)
        self.assertEqual(id(s1), id(s0.checkAttr('a', None)), "Failed to return correct state")
        s0.matchIndice(1, s1)
        self.assertEqual(id(s1), id(s0.checkIndice(1, None)), "Failed to return correct state")
        s0.matchKey('tutu', s1)
        self.assertEqual(id(s1), id(s0.checkKey('tutu', None)), "Failed to return correct state")
        s0.matchValue('tutu', s1)
        self.assertEqual(id(s1), id(s0.checkValue('tutu', None)), "Failed to return correct state")
        s0.matchType(int, s1)
        self.assertEqual(id(s1), id(s0.checkType(int, None)), "Failed to return correct state")
        s0.matchDefault(s1)
        self.assertEqual(id(s1), id(s0.doDefault(None)), "Failed to return correct state")
        #   Event
        s0.matchEvent('lolo', s1)
        self.assertEqual(id(s1), id(s0.doDefaultEvent(None)), "Failed to return correct state")
        #   Hook
        def dummy(self, t):
            pass
        s0.matchHook(dummy, s1)
        sh = s0.default_hook
        self.assertTrue(type(sh) is StateHook, "Failed to return correct state")
        self.assertEqual(id(s1), id(s0.doDefaultHook(None)), "Failed to return correct state")

    def test_01(self):
        """Event Expr event"""
        nsr = StateRegister()
        s0 = State(nsr)
        s1 = State(nsr)
        s2 = State(nsr)
        # set one event
        s1.matchEvent('lolo', s0)
        sX = s1.doDefaultEvent(None)
        self.assertEqual(id(s0), id(sX), "Failed to init the event for the test")
        # check if is set
        e = EventNamed('lolo')
        s2 = State(nsr)
        s0.matchEventExpr(e, s2)
        self.assertEqual(id(s2), id(s0.checkEventExpr(None)), "Failed to return correct state")
        # lala & lulu
        s0.cleanAll()
        s3 = State(nsr)
        s3.matchEvent('lala', s0)
        s3.doDefaultEvent(None)
        e = EventSeq([EventNamed('lala'), EventNamed('lulu')])
        s0.matchEventExpr(e, s2)
        sX = s0.checkEventExpr(None)
        self.assertTrue(id(s2) != id(sX), "Failed to return correct state")
        s4 = State(nsr)
        s4.matchEvent('lulu', s0)
        s4.doDefaultEvent(None)
        self.assertTrue(id(s2) == id(s0.checkEventExpr(None)), "Failed to return correct state")
        # lala & !lulu
        s0.events_expr = list()
        s0.cleanAll()
        s3.matchEvent('lala', s0)
        s3.doDefaultEvent(None)
        s4.matchEvent('lulu', s0)
        s4.doDefaultEvent(None)
        e = EventSeq([EventNamed('lala'), EventNot(EventNamed('lulu'))])
        s0.matchEventExpr(e, s2)
        sX = s0.checkEventExpr(None)
        self.assertTrue(id(s2) != id(sX), "Failed to return correct state")
        s0.cleanAll()
        s3.matchEvent('lala', s0)
        s3.doDefaultEvent(None)
        sX = s0.checkEventExpr(None)
        self.assertTrue(id(s2) == id(sX), "Failed to return correct state")
        # lala | lulu
        s0.events_expr = list()
        s0.cleanAll()
        s4.matchEvent('lulu', s0)
        s4.doDefaultEvent(None)
        e = EventAlt([EventNamed('lala'), EventNamed('lulu')])
        s0.matchEventExpr(e, s2)
        sX = s0.checkEventExpr(None)
        self.assertTrue(id(s2) == id(sX), "Failed to return correct state")
        # lala & ( lolo | lulu)
        s0.events_expr = list()
        nsr.resetEvents()
        s3.matchEvent('lala', s0)
        s3.doDefaultEvent(None)
        s4.matchEvent('lulu', s0)
        s4.doDefaultEvent(None)
        e = EventSeq([EventNamed('lala'), EventAlt([EventNamed('lolo'), EventNamed('lulu')])])
        s0.matchEventExpr(e, s2)
        sX = s0.checkEventExpr(None)
        self.assertTrue(id(s2) == id(sX), "Failed to return correct state")

    def test_03(self):
        """basic tree matching"""
        class Test:
            pass
        def checkMatch(tree: Node, user_data) -> Node:
            user_data[1].assertEqual(user_data[0], id(tree), "Failed to match the node of tree")
            return tree
        def checkNoMatch(tree: Node, user_data) -> Node:
            return tree

        # Test(.b = 42) -> #checkMatch;
        m = MatchBlock([
            MatchHook(checkMatch, MatchType(Test, [MatchAttr('b', MatchValue(42))])),
        ])
        tree = StateSeqBuilder()
        nsr = StateRegister()
        m.build_state_tree(tree, nsr)
        nsr.label = repr(m)
        nsr.to_png_file(rpath + os.sep + 't1.png')
        t = Test()
        t.b = 42
        s = walk(t, nsr.default, (id(t), self))
        self.assertEqual(id(s), id(nsr.default), 'Failed to reset the state to s0')
        # Test(.b = 42) -> #checkNoMatch;
        m = MatchBlock([
            MatchHook(checkNoMatch, MatchType(Test, [MatchAttr('b', MatchValue(42))])),
        ])
        tree = StateSeqBuilder()
        nsr = StateRegister()
        m.build_state_tree(tree, nsr)
        nsr.label = repr(m)
        nsr.to_png_file(rpath + os.sep + 't2.png')
        t = Test()
        t.a = 42
        t.b = 12
        s = walk(t, nsr.default, (id(t), self))
        self.assertEqual(id(s), id(nsr.default), 'Failed to reset the state to s0')
        # Test(.a=42, .c=1.2) -> #checkMatch;
        m = MatchBlock([
            MatchHook(checkMatch, MatchType(Test, [MatchAttr('a', MatchValue(42)), MatchAttr('c', MatchValue(1.2))])),
        ])
        tree = StateSeqBuilder()
        nsr = StateRegister()
        m.build_state_tree(tree, nsr)
        nsr.label = repr(m)
        nsr.to_png_file(rpath + os.sep + 't3.png')
        t = Test()
        t.a = 42
        t.c = 1.2
        s = walk(t, nsr.default, (id(t), self))
        self.assertEqual(id(s), id(nsr.default), 'Failed to reset the state to s0')
        t = Test()
        t.a = 42
        t.b = Test()
        t.b.c = 1.2
        s = walk(t, nsr.default, (id(t), self))
        self.assertEqual(id(s), id(nsr.default), 'Failed to reset the state to s0')
