import unittest
from pyrser.grammar import Grammar


class CompositionMath(Grammar):
    grammar = """
      operand ::=  #num '+' #num
      ;
      """
#      def __init__(self):
#          super(CompositionMath, self).__init__(CompositionMath,
#                                     CompositionMath.__doc__,
#                                     globals())


class Composition(Grammar):
    grammar = """
      composition ::= CompositionMath::operand
      ;
      """
    globals = globals()

#      def __init__(self):
#          super(Composition, self).__init__(Composition,
#                                            Composition.__doc__,
#                                            globals())
#          CompositionMath() # for composition we need an instance


class generatedCode(unittest.TestCase):
    @classmethod
    def setUpClass(cGeneratedCodeClass):
        cGeneratedCodeClass.oRoot = {}
        cGeneratedCodeClass.oGrammar = Composition()

    def test_composition(self):
        self.assertEqual(
            generatedCode.oGrammar.parse('12 + 12', self.oRoot, 'composition'),
            True,
            'failed in composition')
