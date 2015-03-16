import unittest
from pyrser.ast.state import *
from pyrser.ast.walk import *
from pyrser.ast.match import *


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
        s0.matchDefault(None)
        s0.matchEvent('lolo', s1)
        self.assertEqual(id(s1), id(s0.doDefault(None)), "Failed to return correct state")
        #   Hook
        def dummy(self, t):
            pass
        s0.matchDefault(None)
        s0.matchHook(dummy, s1)
        sh = s0.default
        self.assertTrue(type(sh) is StateHook, "Failed to return correct state")
        self.assertEqual(id(s1), id(s0.doDefault(None)), "Failed to return correct state")
