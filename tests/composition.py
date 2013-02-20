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
