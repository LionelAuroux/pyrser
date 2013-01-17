# Copyright (C) 2012 Candiotti Adrien
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

from pyrser.code_generation.procedural import *
from pyrser.code_generation.docstring import Docstring


class Python(Procedural):
    def __init__(self, dLangConf):
        super(Python, self).__init__(dLangConf)
        self.__oDocstring = Docstring(self)

    def lang_range(self, range):
        if not self.oHelper.inRecurse():
            self.sRes += self.oHelper.baseParserAccess()
        self.sRes += ("%s(%s, %s)" %
                     (self.capitalizeIfRecurse(self.oHelper.builtin('range')),
                      range['from'], range['to']))

    def lang_directive(self, directive):
        self.sRes += ("%s%s" % (self.oHelper.baseParserAccess(),
                                self.oHelper.builtin(directive['name'])))
        if not self.oHelper.inRecurse():
            self.sRes += "()"

    def lang_nonTerminal(self, nonTerminal):
        if not self.oHelper.inRecurse():
            self.sRes += ("%s%sRule(oNode)" % (self.oHelper.accessInstance(),
                                               nonTerminal['name']))
        else:
            self.sRes += "NonTerminal(%s%sRule, oNode)" % (
                self.oHelper.accessInstance(), nonTerminal['name'])

    def lang_wrapper(self, wrapper):
        if not self.oHelper.inRecurse():
            self.sRes += "%s%sWrapper" % (self.oHelper.accessInstance(),
                                          wrapper['name'])
            self.unary(wrapper)
            self.sRes += ",oNode"
        else:
            self.sRes += "Hook(%s%sWrapper," % (self.oHelper.accessInstance(),
                                                wrapper['name'])
            self.unary(wrapper, False)
            self.sRes += "),oNode"
        if "param" in wrapper:
            self.sRes += ", %s" % wrapper['param']
        self.sRes += ")"

    def lang_hook(self, hook):
        if not self.oHelper.inRecurse():
            self.sRes += "%s%sHook(oNode" % (self.oHelper.accessInstance(),
                                             hook['name'])
            if "param" in hook:
                self.sRes += ", %s" % hook['param']
        else:
            self.sRes += "Hook("
            self.sRes += self.oHelper.accessInstance()
            self.sRes += "%sHook, oNode" % hook['name']
            if "param" in hook:
                self.sRes += ", %s" % hook['param']
        self.sRes += ")"

    def lang_aggregation(self, aggregation):
        if self.oHelper.inRecurse():
            self.sRes += ("NonTerminal(%s()%s%sRule, oNode)" %
                         (aggregation['name'],
                          self.oHelper.accessOperator(),
                          aggregation['nonTerminal']['name']))
        else:
            self.sRes += ("%s()%s%sRule(oNode)" %
                         (aggregation['name'],
                          self.oHelper.accessOperator(),
                          aggregation['nonTerminal']['name']))

    def lang_cchar(self, char):
        if not self.oHelper.inRecurse():
            self.sRes += self.oHelper.baseParserAccess()
        self.sRes += self.capitalizeIfRecurse(
            self.oHelper.builtin('readThisChar'))
        self.sRes += "(%s)" % char['string']

    def lang_cstring(self, text):
        if not self.oHelper.inRecurse():
            self.sRes += self.oHelper.baseParserAccess()
        self.sRes += self.capitalizeIfRecurse(
            self.oHelper.builtin('readThisText'))
        self.sRes += "(%s)" % text['string']

    def lang_rule_directive(self, rule):
        if 'rule_directive' in rule['prototype']:
            for rule_directive in rule['prototype']['rule_directive']:
                self.sRes += "      @%s" % rule_directive['name']
                if 'param' in rule_directive:
                    self.sRes += "(%s)" % {{rule_directive.param}}
                self.sRes += "\n"

    def lang_rule(self, grammar_name, rule):
        self.oHelper.setGlobal('current_rule', rule['prototype']['name'])
#      @staticmethod
        self.sRes += """
      @parsingContext
      @node.node('%s')
"""          % rule['prototype']['name']
        self.lang_rule_directive(rule)
        self.sRes +=\
            """      def %sRule(self, oNode):
          \"\"\"
          """ % rule['prototype']['name']
        self.sRes += self.__oDocstring.lang_rule(grammar_name, rule)
        self.sRes += '''          """
          return (True
'''
        self.browse_rule(rule, self.lang_clauses)
        self.sRes += ")\n"

    def translation(self, sGrammarName, lRules):
        self.sRes = """class CompiledGrammar:\n"""
        self.browse_rules(sGrammarName, lRules, self.lang_rule)
        return self.sRes
