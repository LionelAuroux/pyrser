import unittest
from pyrser.grammar import Grammar

"""
This set of test check if the grammar is correctly generated in tests
that implies expression imbrications.
"""


class MultiDepthGeneration(Grammar):
    grammar = """
      directive ::= [#identifier #string #num]
        ;

      capture ::= [#identifier : c #identifier : c #identifier : c]
        ;

      hook ::= [#test #test2 #test3]
        ;

      wrapper ::=  	@test #identifier :test
		  [ ',' @test #identifier :test ]*
	;

      nonTerminal ::= [directive directive directive]
        ;

      range ::= ['a' .. 'z' '0' .. '9' 'A' .. 'Z']
        ;

      until ::= [->'1' ->'2' ->'3']
        ;

      multiplier ::= [['1']? ['2']? ['3']?]
        ;

      not ::= [!"toto" #identifier !"tata" #identifier !"titi" #identifier]
        ;

      alt ::= [[#identifier | #num] [ #char | #string] [#cchar | #notIgnore]]
        ;

      terminal_range1 ::= ['0'{1} '1'{2} '2'{3}]
        ;

      terminal_range2 ::= ['0'{1, 3} '1'{2, 4} '2'{4, 6}]
        ;
      """
#      def __init__(self):
#          super(MultiDepthGeneration, self).__init__(MultiDepthGeneration,
#						     MultiDepthGeneration.__doc__)

    def testHook(self, oNode):
        return True

    def test2Hook(self, oNode):
        return True

    def test3Hook(self, oNode):
        return True

    def testWrapper(self, oRule, oNode):
        if 'list' not in oNode:
            oNode['list'] = []
        bRes = oRule()
        oNode['list'].append(oNode['test'])
        del oNode['test']
        return bRes


class generatedCode(unittest.TestCase):
    @classmethod
    def setUpClass(cGeneratedCodeClass):
        cGeneratedCodeClass.oRoot = {}
        cGeneratedCodeClass.oGrammar = MultiDepthGeneration()

    def test_directive(self):
        self.assertEqual(
            generatedCode.oGrammar.parse(
                'id "ok" 123', self.oRoot, 'directive'),
            True,
            'failed in directive')

    def test_capture(self):
        self.assertEqual(
            generatedCode.oGrammar.parse('id id2 id3', self.oRoot, 'capture'),
            True,
            'failed in capture')

    def test_hook(self):
        self.assertEqual(
            generatedCode.oGrammar.parse('', self.oRoot, 'hook'),
            True,
            'failed in hook')

    def test_wrapper(self):
        generatedCode.oGrammar.parse('foo, bar, rab', self.oRoot, 'wrapper'),
        self.assertEqual(self.oRoot['list'] == ['foo', 'bar', 'rab'],
                         True,
                         'failed in hook')

    def test_range(self):
        self.assertEqual(
            generatedCode.oGrammar.parse('i 8 U', self.oRoot, 'range'),
            True,
            'failed in range')

    def test_nonTerminal(self):
        self.assertEqual(
            generatedCode.oGrammar.parse('id "ok" 123 id "ko" 456 la "to" 789',
                                         self.oRoot, 'nonTerminal'),
            True,
            'failed in nonTerminal')

    def test_until(self):
        self.assertEqual(
            generatedCode.oGrammar.parse('155525553', self.oRoot, 'until'),
            True,
            'failed in nonTerminal')

    def test_multiplier(self):
        self.assertEqual(
            generatedCode.oGrammar.parse('123', self.oRoot, 'multiplier'),
            True,
            'failed in multiplier')

    def test_not(self):
        self.assertEqual(
            generatedCode.oGrammar.parse('lol ok haha', self.oRoot, 'not'),
            True,
            'failed in not')

#      def test_complement(self):
#          self.assertEqual(
#	      generatedCode.oGrammar.parse('01 0022 000333', self.oRoot, 'not'),
#	      True,
#	      'failed in complement')

    def test_alt(self):
        self.assertEqual(
            generatedCode.oGrammar.parse("id a 'a'", self.oRoot, 'alt'),
            True,
            'failed in alt')

    def test_terminal_range1(self):
        self.assertEqual(
            generatedCode.oGrammar.parse("0 11 222", self.oRoot,
                                         'terminal_range1'),
            True,
            'failed in terminal_range #1')

    def test_terminal_range2(self):
        self.assertEqual(
            generatedCode.oGrammar.parse("00 111 22222", self.oRoot,
                                         'terminal_range2'),
            True,
            'failed in terminal_range #2')
