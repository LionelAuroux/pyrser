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

from pyrser.code_generation.browse_grammar import BrowseGrammar


class Procedural(BrowseGrammar):
    def __init__(self, dLangConf):
        super(Procedural, self).__init__(dLangConf)

    def wrap_context(self, oCallback, oArgument):
        self.oHelper.pushCount(0, 1)
        self.oHelper.incDepth()
        self.oHelper.pushAlt(False)
        oCallback(oArgument)
        self.oHelper.popAlt()
        self.oHelper.decDepth()
        self.oHelper.popCount()

    def addOpenParenthesis(self, oTarget):
        if oTarget['terminal']['type'] in ('multiplier', 'alt'):
            self.sRes += "(\\\n"
            self.lang_terminal(oTarget['terminal'])
        else:
            self.sRes += "("
            self.lang_terminal(oTarget['terminal'], False)

    def unary(self, oTarget, bNewline=True):
        self.wrap_context(self.addOpenParenthesis, oTarget)
        if oTarget['terminal']['type'] in ('multiplier', 'alt', 'terminal_range')\
                and bNewline:
            self.sRes += "\n"
            self.sRes += self.oHelper.indent()

    def capitalizeIfRecurse(self, sToCapitalize):
        if self.oHelper.inRecurse():
            return self.oHelper.capitalize(sToCapitalize)
        return sToCapitalize

    def lang_alternative_terminal(self, oAlt):
        self.sRes += self.capitalizeIfRecurse(self.oHelper.alt())
        self.sRes += '(\\\n'
        self.oHelper.pushAlt(True, len(oAlt['alternatives']))
        self.oHelper.incDepth()
        self.browse_clauses(oAlt)
        self.sRes += ')'
        self.oHelper.decDepth()
        self.oHelper.popAlt()

    def lang_terminal_range(self, terminal):
        self.sRes +=\
            self.capitalizeIfRecurse(self.oHelper.multiplier('{}'))
        self.unary(terminal)
        self.sRes += ", %s" % terminal['from']
        if 'to' in terminal:
            self.sRes += ", %s" % terminal['to']
        self.sRes += ")"

    def lang_not(self, negation):
        self.sRes +=\
            self.capitalizeIfRecurse(self.oHelper.not_(negation['not']))
        self.unary(negation, False)
        self.sRes += ")"

    def lang_multiplier(self, multiplier):
        self.sRes +=\
            self.capitalizeIfRecurse(
                self.oHelper.multiplier(multiplier['multiplier']))
        if multiplier['multiplier'] == '[]':
            self.sRes += '(\\\n'
            self.wrap_context(self.browse_clauses,
                              multiplier['terminal']['clauses'])
        else:
            self.unary(multiplier, False)
        self.sRes += ")"

    def lang_capture(self, capture):
        self.sRes += self.capitalizeIfRecurse('capture')
        self.unary(capture)
        self.sRes += ', "%s", oNode)' % capture['name']

    def lang_until(self, until):
        self.sRes += self.capitalizeIfRecurse('until')
        self.unary(until, False)
        self.sRes += ')'

    def lang_lookAhead(self, look_ahead):
        self.sRes += capitalizeIfRecurse('lookAhead')
        unary(look_ahead, False)
        self.sRes += ')'

    def lang_syntax(self, indent=True):
        if indent == True:
            self.sRes += self.oHelper.indent()
        if not self.oHelper.inRecurse():
            self.sRes += self.oHelper.keyword('and')
        if self.oHelper.inRecurse()\
            and (self.oHelper.count() > 0
                 or self.oHelper.altCount() > 0):
            self.sRes += ","
        else:
            self.sRes += " "

    def lang_terminal(self, terminal, indent=True):
        self.lang_syntax(indent)
        getattr(self, 'lang_%s' % terminal['type'])(terminal)
        if self.oHelper.count() < self.oHelper.length() - 1\
                or self.oHelper.altCount() < self.oHelper.altLength() - 1:
            self.sRes += "\\\n"
            self.oHelper.incCount()

    def lang_alternative(self, loop, alternative):
        self.oHelper.pushCount(0, len(alternative))
        self.browse_alternative(alternative)
        self.oHelper.incAltCount()
        self.oHelper.popCount()

    def lang_clauses(self, clauses):
        self.oHelper.pushAlt(False)
        self.browse_clauses(clauses)
        self.oHelper.popAlt()
