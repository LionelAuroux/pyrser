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
from functools import wraps
from pyrser.grammar import Grammar


def test(oRule):
    def wrapper(*lArgs):
        bRes = oRule(*lArgs)
        lArgs[1]['rule_directive_test'] = True
        return bRes
    return wrapper


class RuleDirective(Grammar):
    grammar = """
      rule_directive @test ::= #identifier
      ;
      """
    globals = globals()
#      def __init__(self):
#          super(RuleDirective, self).__init__(RuleDirective,
#					      RuleDirective.__doc__, globals())


class generatedCode(unittest.TestCase):
    @classmethod
    def setUpClass(oCls):
        generatedCode.oGrammar = RuleDirective()
        generatedCode.oRoot = {}

    def test_rule_directive(self):
        generatedCode.oGrammar.parse('identifier',
                                     self.oRoot, 'rule_directive'),
        self.assertEqual(
            self.oRoot['rule_directive_test'],
            True,
            'failed in rule_directive')
