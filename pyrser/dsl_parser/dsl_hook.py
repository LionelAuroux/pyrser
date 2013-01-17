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

from pyrser.node import new_node
from pyrser.dsl_parser.dsl_error import GrammarException

# FIXME : erase all 'del' : usefull for debug, nothing more

"""
Hook called to build the tree/work on the stream.
"""
dBuiltins =\
    ('identifier', 'num', 'string', 'cchar', 'char',
        'space', 'end', 'empty', 'super', 'notIgnore',
        'resetIgnore')


def injectExpression(lAlternative):
    return [{'multiplier': '[]',
             'terminal': {'clauses': {'alternatives': [lAlternative],
                                      'type': 'clause'},
                          'type': 'expr'},
             'type': 'multiplier'}]


def injectAlternative(oNode):
    if len(oNode['clauses']['alternatives']) > 1:
        oNode['clauses']['alternatives'] =\
            [[{'alternatives': oNode['clauses']['alternatives'],
             'type': 'alternative_terminal'}]]
    return oNode


def injectUnaryTerminal(oNode, sField):
    oTmp = new_node(None, sField)
    oTmp[sField] = oNode[sField]
    oTmp['terminal'] = oNode['terminal']
    oNode['terminal'] = oTmp


def injectAggregated(oNode):
    if 'aggregation' in oNode:
        oTmp = new_node(oNode['parent'], 'aggregation')
        oTmp['name'] = oNode['name']
        oNode['name'] = oNode['aggregation']
        oTmp['nonTerminal'] = oNode
        del oNode['aggregation']
        del oNode['parent']
        oNode = oTmp
    return oNode


def swapTerminal(oNode):
    oTmp = oNode['parent']['terminal']
    oNode['terminal'] = oTmp
    oNode['parent']['terminal'] = oNode


def rulesHook(oNode):
    if 'rules' not in oNode['parent']:
        oNode['parent']['rules'] = []

    oNode = injectAlternative(oNode)
    oNode['parent']['rules'].append(oNode)
    return True


def rule_nameHook(oNode):
    oNode['parent']['prototype'] = oNode
    return True


def paramHook(oNode):
    oNode['parent']['param'] = oNode['param'][1:-1]
    return True


def rule_directiveHook(oNode):
    if 'rule_directive' not in oNode['parent']:
        oNode['parent']['rule_directive'] = []
    oNode['parent']['rule_directive'].append(oNode)
    return True


def headclausesHook(oNode):
    oNode['alternatives'] = [[]]
    return True


def tailclausesHook(oNode):
    oNode['alternatives'].append([])
    return True


def clausesHook(oNode):
    if len(oNode['alternatives']) > 1:
        nIndex = 0
        for iAlternative in oNode['alternatives']:
            if len(iAlternative) > 1:
                oNode['alternatives'][nIndex] = injectExpression(iAlternative)
            nIndex += 1
    oNode['parent']['clauses'] = oNode
    return True


def alternativeHook(oNode):
    if 'wrapper' in oNode:
        oNode['type'] = 'wrapper'
        injectUnaryTerminal(oNode, 'wrapper')
        if 'param' in oNode:
            oNode['terminal']['param'] = oNode['param']
            del oNode['param']
        oNode['terminal']['name'] = oNode['name']
        del oNode['wrapper']

    oNode['parent']['alternatives'][-1].append(oNode['terminal'])
    return True


def nonTerminalHook(oNode):
    oNode = injectAggregated(oNode)

    oNode['parent']['terminal'] = oNode
    del oNode['parent']
    return True


def aggregationHook(oNode):
    del oNode['parent']
    return True


def terminalHook(oNode):
    for iController in ('multiplier', 'not'):
        if iController in oNode:
            injectUnaryTerminal(oNode, iController)

    oNode['parent']['terminal'] = oNode['terminal']
    return True


def directiveHook(oNode):
    if oNode['name'] not in dBuiltins:
        oNode['type'] = 'hook'
    elif 'param' in oNode:
        raise GrammarException\
            ("Using parameters on a builtin directive : %s." % oNode['name'])
    if oNode['name'] == 'super':
        oNode['type'] = 'super'
    oNode['parent']['terminal'] = oNode
    del oNode['parent']
    return True


def cStringHook(oNode):
    if len(oNode['string'][1:-1]) == 0:
        raise GrammarException('Using an empty string as string literal.')
    oNode['parent']['terminal'] = oNode
    del oNode['parent']
    return True


def checkCCharLength(cChar):
    if len(cChar[1:-1]) > 1 and cChar[1] != '\\':
        raise GrammarException\
            ('Using a char literal which length is greater than 1 : %s'
             % cChar)
    elif len(cChar[1:-1]) == 0:
        raise GrammarException('Using an empty string as char literal.')

# FIXME : worst bug a ' alone make the readuntil fail and consume a big
# chunk of waste memory.


def cCharHook(oNode):
    checkCCharLength(oNode['string'])
    oNode['parent']['terminal'] = oNode
    del oNode['parent']
    return True


def rangeHook(oNode):
    checkCCharLength(oNode['from'])
    checkCCharLength(oNode['to'])
    if ord(oNode['from'][1:-1]) > ord(oNode['to'][1:-1]):
        raise GrammarException\
            ('Range : first character should be < to second : %s > %s' %
            (oNode['from'], oNode['to']))
    oNode['parent']['terminal'] = oNode
    del oNode['parent']
    return True


def exprHook(oNode):
    oNode = injectAlternative(oNode)
    oExpression = {'type': 'multiplier',
                   'multiplier': '[]',
                   'terminal': oNode}
    oNode['parent']['terminal'] = oExpression
    del oNode['parent']
    return True


def untilHook(oNode):
    oNode['parent']['terminal'] = oNode
    del oNode['parent']
    return True


def lookAheadHook(oNode):
    oNode['parent']['terminal'] = oNode
    del oNode['parent']
    return True


def read_terminalRangeHook(oNode):
    swapTerminal(oNode)
    oNode['multiplier'] = '{}'
    oNode['type'] = 'terminal_range'
    del oNode['parent']
    return True


def captureHook(oNode):
    swapTerminal(oNode)
    del oNode['parent']
    return True
