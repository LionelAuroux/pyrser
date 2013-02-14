# Copyright (C) 2012 Candiotti Adrien
# Copyright (C) 2013 Pascal Bertrand
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
from pyrser.grammar import Grammar


class Father(Grammar):
    grammar = """
      operand ::= #num
      ;

      sub ::= #identifier
      ;
      """
#      def __init__(self):
#          super(Father, self).__init__(Father, Father.__doc__, globals())


class Math(Father, Grammar):
    grammar = """
      operand ::= Father::operand '+' sub
      ;

      sub ::= #num
      ;
      """
    globals = globals()
#      def __init__(self):
#          Grammar.__init__(self, Math, Math.__doc__, globals())


class MultiMath(Father, Grammar):
    grammar = """
      operand ::=  Father::operand ['+' Father::operand ]+
      ;
      """
    globals = globals()
#      def __init__(self):
#          Grammar.__init__(self, MultiMath, MultiMath.__doc__, globals())
#          Father() # for composition we need an instance


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
