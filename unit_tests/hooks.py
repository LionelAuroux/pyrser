import unittest
from pyrser.grammar import Grammar
from pyrser.hooks import GenericHook
from pyrser.node import clean_tree

"""
This set of test check the generic hook class.
"""


class GenericHookTest(GenericHook, Grammar):
    grammar = """
      _ ::= @_ sub
      ;

      next ::= @next("bar") sub
      ;

      push_at ::= @push_at("subs") sub [ ',' @push_at("subs") sub]*
      ;

      push_capture_at ::=         @push_capture_at("subs", "sub") sub
                          [ ',' @push_capture_at("subs", "sub") sub]*
      ;

      continue ::= [sub]? stack_trace_test
      ;

      stack_trace_test ::= @continue("La regle Sub a foire!") sub
      ;

      trace_hook ::= level1
      ;

      trace_wrapper ::= @trace('trace_wrapper') [level_1 sub level_1]
      ;

      /* These are used for the tests */
      level1 ::= level2
      ;

      level2 ::= #trace
      ;

      level_1 ::= level_2
      ;

      level_2 ::= level_3
      ;

      level_3 ::= #true
      ;

      consumed_wrapper ::= @consumed("test") sub
      ;

      sub ::= #identifier :sub
      ;
      """
#      def __init__(self):
#          Grammar.__init__(self, GenericHookTest, GenericHookTest.__doc__)


class GenericHookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cGeneratedCodeClass):
        cGeneratedCodeClass.oRoot = {}
        cGeneratedCodeClass.oGrammar = GenericHookTest()

    def test__Wrapper(self):
        GenericHookTests.oGrammar.parse('foo', self.oRoot, '_'),
        self.assertEqual(self.oRoot['sub'], 'foo', 'failed in @_')
        self.assertEqual(
            id(self.oRoot) in self.oRoot, False, 'failed in @_')

    def test_nextWrapper(self):
        self.oRoot = {}
        GenericHookTests.oGrammar.parse('foo', self.oRoot, 'next'),
        self.assertEqual(self.oRoot['bar']['sub'], 'foo', 'failed in @next')
        self.assertEqual(id(self.oRoot) in self.oRoot, False,
                         'failed in @next')

    def test_push_atWrapper(self):
        self.oRoot = {}
        GenericHookTests.oGrammar.parse('foo, bar, rab, oof',
                                        self.oRoot, 'push_at'),
        clean_tree(self.oRoot, 'parent')
        clean_tree(self.oRoot, 'type')
        self.assertEqual(self.oRoot['subs'], [{'sub':'foo'},
                                              {'sub': 'bar'},
                                              {'sub': 'rab'},
                                              {'sub': 'oof'}],
                         'failed in @push_at')
        self.assertEqual(id(self.oRoot) in self.oRoot, False,
                         'failed in @push_at')

    def test_push_capture_at(self):
        self.oRoot = {}
        GenericHookTests.oGrammar.parse('foo, bar, rab, oof',
                                        self.oRoot, 'push_capture_at'),
        self.assertEqual(self.oRoot['subs'], ['foo', 'bar', 'rab', 'oof'],
                         'failed in @push_capture_at')
        self.assertEqual(id(self.oRoot) in self.oRoot, False,
                         'failed in @push_capture_at')

    def test_continue(self):
        self.oRoot = {}
        try:
            GenericHookTests.oGrammar.parse(
                'id1 123 id3', self.oRoot, 'continue')
        except:
            print("THIS EXCEPTION IS PART OF THE TEST.")

# Visual tests
#      def test_trace_hook(self):
#          GenericHookTests.oGrammar.parse('', self.oRoot, 'trace_hook')

#      def test_trace_wrapper(self):
#          GenericHookTests.oGrammar.parse('foo', self.oRoot, 'trace_wrapper')

#      def test_consumed_wrapper(self):
# GenericHookTests.oGrammar.parse('foo', self.oRoot, 'consumed_wrapper')
