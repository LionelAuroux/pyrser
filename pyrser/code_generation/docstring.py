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

from pyrser.code_generation.browse_grammar import *


class Docstring(BrowseGrammar):
    def __init__(self, oRenderer):
        super(Docstring, self).__init__(oRenderer.dLangConf)
        self.sRes = ""

    def lang_multiplier(self, multiplier):
        if multiplier['multiplier'] == '[]':
            self.sRes += " ["
            self.browse_clauses(multiplier['terminal']['clauses'])
            self.sRes += " ]"
        else:
            self.lang_terminal(multiplier['terminal'])
            self.sRes += multiplier['multiplier']

    def lang_directive(self, terminal):
        self.sRes += " #%s" % terminal['name']

    def lang_capture(self, terminal):
        self.lang_terminal(terminal['terminal'])
        self.sRes += " :%s" % terminal['name']

    def lang_nonTerminal(self, terminal):
        self.sRes += " %s" % terminal['name']

    def lang_hook(self, terminal):
        self.sRes += " %%%s" % terminal['name']

    def lang_wrapper(self, terminal):
        self.sRes += " @%s" % terminal['name']
        self.lang_terminal(terminal['terminal'])

    def lang_until(self, terminal):
        self.sRes += " ->"
        self.lang_terminal(terminal['terminal'])

    def lang_lookAhead(self, terminal):
        self.sRes += " ="
        self.lang_terminal(terminal['terminal'])

    def lang_cchar(self, terminal):
        self.sRes += " %s" % terminal['string']

    def lang_cstring(self, terminal):
        self.sRes += ' %s' % terminal['string']

    def lang_not(self, terminal):
        self.sRes += " %s" % terminal['not']
        self.lang_terminal(terminal['terminal'])

    def lang_aggregation(self, terminal):
        self.sRes +=\
            " %s::%s" % (terminal['name'], terminal['nonTerminal']['name'])

    def lang_alternative_terminal(self, terminal):
        self.browse_clauses(terminal)

    def lang_range(self, terminal):
        self.sRes += " %s .. %s" % (terminal['from'], terminal['to'])

    def lang_terminal_range(self, terminal):
        self.lang_terminal(terminal['terminal'])
        self.sRes += "{%s" % (terminal['from'])
        if 'to' in terminal:
            self.sRes += ", %s}" % (terminal['to'])
        else:
            self.sRes += "}"

    def lang_terminal(self, terminal):
        getattr(self, 'lang_%s' % terminal['type'])(terminal)
        pass

    def lang_alternative(self, nCount, lAlternative):
        if nCount > 0:
            self.sRes += " |"
        self.browse_alternative(lAlternative)

    def lang_clauses(self, clauses):
        self.browse_clauses(clauses)

    def lang_rule_directive(self, rule_directive):
        self.sRes += " @%s" % rule_directive['name']
        if 'params' in rule_directive:
            self.sRes += "(%s" % rule_directive['params']

    def lang_template_rule_name(self, rule):
        """
        if rule.prototype.has_key('template'):
          if rule.prototype.template.string == '?':
            <{{rule.prototype.template.string}}>
        else:
          <"{{rule.prototype.template.string}}">
        """

    def lang_rule(self, grammar_name, rule):
        self.sRes = "%s::%s" % (grammar_name, rule['prototype']['name'])
#    	  lang_template_rule_name(rule)
# FIXME
# browse_rule_directives(rule['prototype']['rule_directive'],
# lang_rule_directive)
        self.sRes += " ::="
        self.browse_rule(rule, self.lang_clauses)
        self.sRes += "\n          ;\n"
        return self.sRes
