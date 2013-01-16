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

from pyrser import node
from pyrser.dsl_parser import dsl_parser
from pyrser.code_generation import python

# TODO(bps): factor those imports for generated code
from pyrser.parsing.capture import capture, Capture
from pyrser.parsing.parsing_context import parsingContext, Parsing
from pyrser.parsing.directive_functor import NonTerminal, ReadChar, Hook, ReadText, ReadRange
from pyrser.parsing.bnf_primitives import zeroOrN, Expression, oneOrN, expression, Alt, ZeroOrOne, Negation, N, Until, alt, complement, zeroOrOne, negation, n, until
from pyrser.lang.python import python as dLangConf


class GrammarBase(type):
    """Metaclass for all grammars."""
    def __new__(mcs, name, bases, dict_):
        grammar = dict_.get('grammar')
        if grammar is not None:
            ast = dsl_parser.parse(grammar, {}, name)
            generated_code = (
                python.Python(dLangConf).translation(name, ast['rules']))
            byte_code = compile(generated_code, "<%s>" % name, "exec")
            globals_ = dict_.get('globals')
            if globals_ is None:
                globals_ = globals()
            else:
                globals_.update(globals())
            dict_['globals'] = globals_
            eval(byte_code, globals_, locals())
            compiled_grammar = locals()['CompiledGrammar']
            for key, value in compiled_grammar.__dict__.iteritems():
                if callable(value):
                    dict_[key] = value
        return type.__new__(mcs, name, bases, dict_)


class Grammar(object):
    """
    Base class for all grammars.

    This class turn any class A that inherit it into a grammar.
    Taking the description of the grammar in parameter it will add
    all what is what is needed for A to parse it.
    """

    __metaclass__ = GrammarBase
    grammar = None
    globals = None

    def parse(self, source, ast, rule_name):
        """Parse the grammar"""

        func_name = '%sRule' % rule_name
        node.next_is(ast, ast)
        dsl_parser.Parsing.oBaseParser.parsedStream(source)
        if not hasattr(self, func_name):
            raise Exception("First rule doesn't exist : %s" % func_name)
        result = getattr(self, func_name)(ast)
        if not result:
            return False
        dsl_parser.Parsing.oBaseParser.readWs()
        return dsl_parser.Parsing.oBaseParser.readEOF()
