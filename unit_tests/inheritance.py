import unittest
from pyrser.grammar import Grammar
from pyrser.generic.singleton import Singleton

class Father(Grammar):
      """
      operand ::= #num
      ;

      sub ::= #identifier
      ;
      """
      __metaclass__ = Singleton
      def __init__(self):
	  Grammar.__init__(self, Father, Father.__doc__, globals())

class Math(Father, Grammar):
      """
      operand ::= Father::operand '+' sub
      ;

      sub ::= #num
      ;
      """
      def __init__(self):
	  Father.__init__(self)
          Grammar.__init__(self, Math, Math.__doc__, globals())
	  Father()

class MultiMath(Father, Grammar):
      """
      operand ::=  Father::operand ['+' Father::operand ]+
      ;
      """
      def __init__(self):
	  Father.__init__(self)
	  Grammar.__init__(self, MultiMath, MultiMath.__doc__, globals())

class generatedCode(unittest.TestCase):
      @classmethod
      def setUpClass(cGeneratedCodeClass):
          cGeneratedCodeClass.oRoot = {}
	  cGeneratedCodeClass.oGrammar = Math()

      def test_inheritance(self):
          self.assertEqual(
	      generatedCode.oGrammar.parse('12 + 4', self.oRoot, 'operand'),
	      True,
	      'failed in inheritance')
      
      def test_inheritance_multi_depth(self):
          self.assertEqual(
	      MultiMath().parse('12 + 3 + 5', self.oRoot, 'operand'),
	      True,
	      'failed in multi inheritance')
