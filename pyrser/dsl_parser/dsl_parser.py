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

from pyrser.parsing import *
from pyrser.parsing.parsing_context import parsingContext
from pyrser.parsing.capture import *
from pyrser.parsing.bnf_primitives import *
from pyrser.parsing.directive_functor import *
from pyrser.node import node
from pyrser.dsl_parser.dsl_hook import *
from pyrser.dsl_parser.dsl_error import *


def parse(sSource, oRoot, sCurrentFile):
    """
    Entry point of the BNF parsing.
    """
    Parsing.oBaseParser.parsedStream(sSource, sCurrentFile)

    globalDescRule(oRoot)
    resetBaseParser()
    return oRoot


def globalDescRule(oRoot):
    """
    global_desc ::= [rules]+
    ;
    """
    if not oneOrN(NonTerminal(rulesRule, oRoot)):
        raise GrammarException('%s doesn\'t seems to be a valid grammar file.' %
                               Parsing.oBaseParser.getName())
    Parsing.oBaseParser.readIgnored()
    return Parsing.oBaseParser.readEOF()


@node('rule')
@parsingContext
def rulesRule(oNode):
    """
    rules ::= rule_name "::=" clauses ';'
    ;
    """
    if ruleNameRule(oNode)\
        and alt(ReadText('::='), Error('\'::=\' missing'))\
        and alt(NonTerminal(clausesRule, oNode),
                Error('No clauses found in this rule : %s'
                      % oNode['prototype']['name']))\
        and alt(ReadChar(';'), Error('\';\' missing'))\
            and rulesHook(oNode):
        return True
    return False

# FIXME : how to know if it is name or '{' the pb
#	    	or Error('No name given to current rule.')():
#    and alt(Capture(Parsing.oBaseParser.readIdentifier, 'name', oNode)
#  		,Error('No name given to current rule.'))\


@node('rule_name')
@parsingContext
def ruleNameRule(oNode):
    """
    rule_name ::= #identifier [rule_directive]*
    ;
    """
    if capture(Parsing.oBaseParser.readIdentifier, 'name', oNode)\
        and zeroOrN(NonTerminal(ruleDirectiveRule, oNode))\
            and rule_nameHook(oNode):
        return True
    return False


@node('param')
@parsingContext
def paramRule(oNode):
    """
    param ::= '(' -> ')'
    """
    if capture(Expression(
               ReadChar('('), ReadUntil(')'))        , 'param', oNode)\
            and paramHook(oNode):
        return True
    return False

# FIXME : type is useles, remove after debug


@node('rule_directive')
@parsingContext
def ruleDirectiveRule(oNode):
    """
    rule_directive ::= '@' #identifier [ param ]?
    ;
    """
    if Parsing.oBaseParser.readChar('@')\
        and capture(Parsing.oBaseParser.readIdentifier, 'name', oNode)\
        and zeroOrOne(NonTerminal(paramRule, oNode))\
            and rule_directiveHook(oNode):
        return True
    return False


@node('clause')
@parsingContext
def clausesRule(oNode):
    """
    clauses ::= alternative ['|' alternative ]*
    ;
    """
    if headclausesHook(oNode)\
        and alternativeRule(oNode)\
        and clausesHook(oNode)\
        and zeroOrN(ReadChar('|'),
                    Hook(tailclausesHook, oNode),
                    Alt(
                    Expression(
                        NonTerminal(alternativeRule, oNode),
                        Hook(clausesHook, oNode)),
                    Error(
                    'Alternative found but no clauses in it.'))):
        return True
    return False


@node('capture')
@parsingContext
def captureRule(oNode):
    """
    capture ::= ':' #identifier
    ;
    """
    if Parsing.oBaseParser.readChar(':')\
        and capture(Parsing.oBaseParser.readIdentifier, 'name', oNode)\
            and captureHook(oNode):
        return True
    return False


@node('alternative')
@parsingContext
def alternativeRule(oNode):
    """
    alternative ::= [
                    [ '@' #identifier param ]?
                    [terminal | nonterminal | until | lookAhead ]
                    [capture]?
                  ]+
    ;
    """
    if oneOrN(
        Expression(

            ZeroOrOne(Expression(
                      Capture(ReadChar('@'), 'wrapper', oNode), Capture(
                      Parsing.oBaseParser.readIdentifier, 'name', oNode), ZeroOrOne(
                          NonTerminal(paramRule, oNode)))),

            Alt(
                NonTerminal(terminalRule, oNode),
                NonTerminal(NonTerminalRule, oNode),
                NonTerminal(untilRule, oNode),
                NonTerminal(lookAheadRule, oNode)),

            ZeroOrOne(NonTerminal(captureRule, oNode)),
            Hook(alternativeHook, oNode))):
        return True
    return False


@node('nonTerminal')
@parsingContext
def NonTerminalRule(oNode):
    """
    NonTerminal ::= #identifier [ '.' #identifier ]?
    ;
    """
    if capture(Parsing.oBaseParser.readIdentifier, 'name', oNode)\
        and zeroOrOne(ReadText("::"), Alt(
                      Capture(Parsing.oBaseParser.readIdentifier,
                              'aggregation', oNode)                    , Error('Malformed composed nonTerminal.')))\
            and nonTerminalHook(oNode):
        return True
    return False


@node('directive')
@parsingContext
def directiveRule(oNode):
    """
    directive ::= '#' #identifier [ param ]?
    ;
    """
    if Parsing.oBaseParser.readChar('#')\
        and alt(
            Capture(Parsing.oBaseParser.readIdentifier, 'name', oNode)            , Error('Uncomplete directive.'))\
        and zeroOrOne(NonTerminal(paramRule, oNode))\
            and directiveHook(oNode):
        return True
    return False


@node('cstring')
@parsingContext
def cString(oNode):
    if capture(Parsing.oBaseParser.readCString, 'string', oNode)\
            and cStringHook(oNode):
        return True
    return False


@node('cchar')
@parsingContext
def cChar(oNode):
    if capture(Parsing.oBaseParser.readCChar, 'string', oNode)\
            and cCharHook(oNode):
        return True
    return False


def carRule(oNode):
    """
    car::= '"' ->'"' | "'" -> "'"
    ;
    """
    return alt(NonTerminal(cString, oNode), NonTerminal(cChar, oNode))


@node('range')
@parsingContext
def rangeRule(oNode):
    """
    range ::= car ".." car
    ;
    """
    if capture(Parsing.oBaseParser.readCChar, 'from', oNode)\
        and Parsing.oBaseParser.readText('..')\
        and alt(
            Capture(Parsing.oBaseParser.readCChar, 'to', oNode),
            Error('Range incomplete.'))\
            and rangeHook(oNode):
        return True
    return False


@node('expr')
@parsingContext
def exprRule(oNode):
    """
    expr ::= '[' clauses ']'
    ;
    """
    if Parsing.oBaseParser.readChar('[')\
        and alt(NonTerminal(clausesRule, oNode)                , Error('Empty expression.'))\
        and alt(ReadChar(']')                 , Error('\']\' missing.'))\
            and exprHook(oNode):
        return True
    return False


@node('until')
@parsingContext
def untilRule(oNode):
    """
    until ::= "->" terminal
    ;
    """
    if Parsing.oBaseParser.readText('->')\
        and alt(NonTerminal(terminalRule, oNode), Error(
                'No expression found after until (\'->\') sign.'))\
            and untilHook(oNode):
        return True
    return False


@node('lookAhead')
@parsingContext
def lookAheadRule(oNode):
    """
    lookAhead ::= "=" terminal
    ;
    """
    if Parsing.oBaseParser.readText('=')\
        and alt(NonTerminal(terminalRule, oNode), Error(
                'No expression found after a look ahead (\'=\') sign.'))\
            and lookAheadHook(oNode):
        return True
    return False


@node('terminal')
@parsingContext
def terminalRule(oNode):
    """
    terminal ::=
              ['~'|'!']?
              [directive | expr | range, car]
              [
                ['+'|'?'|'*']
                |
                terminal_range
              ]?
    ;
    """
    if zeroOrOne(Alt(
                 Capture(ReadChar('!'), 'not', oNode)                      , Capture(ReadChar('~'), 'not', oNode)))\
        and alt(NonTerminal(directiveRule, oNode), NonTerminal(exprRule, oNode)                , NonTerminal(rangeRule, oNode)                , NonTerminal(carRule, oNode))\
        and zeroOrOne(
            Alt(
            Alt(
                Capture(ReadChar('*'), 'multiplier',
                        oNode), Capture(ReadChar('+'), 'multiplier', oNode)                , Capture(ReadChar('?'), 'multiplier', oNode)            , NonTerminal(readTerminalRangeRule, oNode))))\
            and terminalHook(oNode):
        return True
    return False

# FIXME : complete error gestion


@node('terminal_range')
@parsingContext
def readTerminalRangeRule(oNode):
    """
    terminal_range = '{' #num ["," #num]? '}'
    ;
    """
    if Parsing.oBaseParser.readChar('{')\
            and alt(
                Capture(Parsing.oBaseParser.readInteger, 'from', oNode)                    , Error('No number found in terminal Range.'))\
            and zeroOrOne(
                ReadChar(','), Alt(
                    Capture(Parsing.oBaseParser.readInteger, 'to', oNode)                      , Error('Second number missing in terminal range.')))\
            and Parsing.oBaseParser.readChar('}')\
            and read_terminalRangeHook(oNode):
        return True
    return False
