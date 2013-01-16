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

from pyrser.code_generation.helper import CodeGenerationHelper


class BrowseGrammar(object):
    def __init__(self, dLangConf):
        self.sRes = ""
        self.dLangConf = dLangConf
        self.oHelper = CodeGenerationHelper(dLangConf)

    def browse_multiplier(self, oMultiplier):
        if oMultiplier['multiplier'] == 'expression':
            browse_clauses(oMultiplier['terminal']['clauses'])
        else:
            browse_terminal(oMultiplier['terminal'])

    def browse_alternative(self, lAlternative):
        for iAlternative in lAlternative:
            self.lang_terminal(iAlternative)

    def browse_clauses(self, lClauses):
        nCount = 0
        for iAlternative in lClauses['alternatives']:
            self.lang_alternative(nCount, iAlternative)
            nCount += 1

    def browse_rule(self, oRule, oCallback):
        oCallback(oRule['clauses'])

    def browse_rule_directives(self, lRule_directives, oCallback):
        for rule_directive in lRule_directives:
            oCallback(rule_directive)

    def browse_hooks(self, oGrammar, oCallback):
        for iHook in oGrammar['hooks']:
            oCallback(oGrammar['name'], iHook)

    def browse_wrappers(self, oGrammar, oCallback):
        for iWrapper in oGrammar['wrappers']:
            oCallback(oGrammar['name'], iWrapper)

    def browse_rules(self, sGrammarName, lRules, oCallback):
        for iRule in lRules:
            oCallback(sGrammarName, iRule)
