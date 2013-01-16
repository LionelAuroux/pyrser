import unittest
from pyrser.grammar import Grammar

"""
This set of test check if the grammar is correctly generated in simple cases,
with no expression imbrications
"""


class NoDepthGeneration(Grammar):
    grammar = """
      directive ::= #identifier
       ;

      capture ::= #identifier : capture
       ;

      hook ::= #test
       ;

      wrapper ::= @test capture
       ;

      nonTerminal ::= directive
       ;

      range ::= 'a' .. 'z'
       ;

      until ::= ->['1']
       ;

      multiplier ::= ['1']?
       ;

      not ::= !"toto" #identifier
       ;

      complement ::= ~'1' '1'
       ;

      alt ::= #identifier | #num
       ;

      terminal_range1 ::= '0'{1}
       ;

      terminal_range2 ::= '0'{1, 3}
       ;
      """
#      def __init__(self):
#          super(NoDepthGeneration, self).__init__(NoDepthGeneration,
#						  NoDepthGeneration.__doc__)

    def testHook(self, oNode):
        return True

    def testWrapper(self, oRule, oNode):
        bRes = oRule()
        oNode['test'] = oNode['capture']
        return bRes


class generatedCode(unittest.TestCase):
    @classmethod
    def setUpClass(cGeneratedCodeClass):
        cGeneratedCodeClass.oRoot = {}
        cGeneratedCodeClass.oGrammar = NoDepthGeneration()

    def test_directive(self):
        self.assertEqual(
            generatedCode.oGrammar.parse(
                'identifier', self.oRoot, 'directive'),
            True,
            'failed in directive')

    def test_capture(self):
        self.assertEqual(
            generatedCode.oGrammar.parse('identifier', self.oRoot, 'capture'),
            True,
            'failed in capture')

    def test_hook(self):
        self.assertEqual(
            generatedCode.oGrammar.parse('', self.oRoot, 'hook'),
            True,
            'failed in hook')

    def test_wrapper(self):
        generatedCode.oGrammar.parse('id', self.oRoot, 'wrapper'),
        self.assertEqual('test' in self.oRoot,
                         True,
                         'failed in wrapper')

    def test_nonTerminal(self):
        self.assertEqual(
            generatedCode.oGrammar.parse(
                'identifier', self.oRoot, 'nonTerminal'),
            True,
            'failed in nonTerminal')

    def test_range(self):
        self.assertEqual(
            generatedCode.oGrammar.parse('i', self.oRoot, 'range'),
            True,
            'failed in range')

    def test_until(self):
        self.assertEqual(
            generatedCode.oGrammar.parse('321', self.oRoot, 'until'),
            True,
            'failed in until')

    def test_multiplier(self):
        self.assertEqual(
            generatedCode.oGrammar.parse('1', self.oRoot, 'multiplier'),
            True,
            'failed in multiplier')

    def test_not(self):
        self.assertEqual(
            generatedCode.oGrammar.parse('tata', self.oRoot, 'not'),
            True,
            'failed in not')

    def test_complement(self):
        self.assertEqual(
            generatedCode.oGrammar.parse('01', self.oRoot, 'complement'),
            True,
            'failed in complement')

    def test_alt(self):
        self.assertEqual(
            generatedCode.oGrammar.parse('123', self.oRoot, 'alt'),
            True,
            'failed in alt')

    def test_terminal_range1(self):
        self.assertEqual(
            generatedCode.oGrammar.parse('0', self.oRoot, 'terminal_range1'),
            True,
            'failed in terminal range #1')

    def test_terminal_range2(self):
        self.assertEqual(
            generatedCode.oGrammar.parse('00', self.oRoot, 'terminal_range2'),
            True,
            'failed in terminal range #2')
