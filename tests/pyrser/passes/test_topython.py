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

import ast
import unittest

from pyrser.code_generation import codegen
from pyrser.parsing.python import parserBase
from pyrser.passes import dumpParseTree
from pyrser.passes import topython


class ParseTreeStub:
    def __init__(self, name):
        self.__name = name

    def topython(self, in_loop=False, in_try=False):
        return ast.Name(self.__name, ast.Load())


#TODO(bps): Fix brittle test suite by testing behavior instead of code
#TODO(bps): Finish testing all nodes
class TestToPythonPasse(unittest.TestCase):
    def test_topython_generates_code_for_call(self):
        method = parserBase.ParserBase.readChar
        call = parserBase.Call(method, 'a')
        res = codegen.to_source(call.topython())
        self.assertEqual(res, "self.readChar('a')")

    def test_topython_generates_code_for_calltrue(self):
        method = parserBase.ParserBase.readChar
        call = parserBase.CallTrue(method, 'a')
        res = codegen.to_source(call.topython())
        self.assertEqual(res, "lambda : (self.readChar('a') or True)")

    def test_topython_generates_code_for_rule(self):
        parser = None
        rule = parserBase.Rule(parser, 'rulename')
        res = codegen.to_source(rule.topython())
        self.assertEqual(res, "self.evalRule('rulename')")

    def test_topython_generates_code_for_hook(self):
        parser = None
        hook = parserBase.Hook(parser, 'hookname')
        res = codegen.to_source(hook.topython())
        self.assertEqual(res,
            "self.evalHook('hookname', self.ruleNodes[(-1)])")

    def test_topython_generates_code_for_clauses(self):
        parser = None
        clauses = parserBase.Clauses(
            parser, ParseTreeStub('a'), ParseTreeStub('b'))
        res = codegen.to_source(ast.Module(clauses.topython()))
        self.assertEqual(res, ("if (not a):\n"
                               "    return False\n"
                               "if (not b):\n"
                               "    return False"))

    def test_topython_generates_code_for_complex_clauses(self):
        parser = None
        clauses = parserBase.Clauses(
            parser,
            ParseTreeStub('a'),
            parserBase.Clauses(parser, ParseTreeStub('b')))
        res = clauses.topython()
        res = codegen.to_source(ast.Module(clauses.topython()))
        self.assertEqual(res, ("if (not a):\n"
                               "    return False\n"
                               "if (not b):\n"
                               "    return False"))

    def test_topython_generates_code_for_alt(self):
        parser = None
        alt = parserBase.Alt(
            parser, ParseTreeStub('a'), ParseTreeStub('b'))
        res = codegen.to_source(ast.Module(alt.topython()))
        self.assertEqual(res, ("try:\n"
                               "    try:\n"
                               "        if (not a):\n"
                               "            raise AltFalse()\n"
                               "        raise AltTrue()\n"
                               "    except AltFalse:\n"
                               "        pass\n"
                               "    try:\n"
                               "        if (not b):\n"
                               "            raise AltFalse()\n"
                               "        raise AltTrue()\n"
                               "    except AltFalse:\n"
                               "        pass\n"
                               "    return False\n"
                               "except AltTrue:\n"
                               "    pass"))

    def test_topython_generates_code_for_complex_alt(self):
        parser = None
        alt = parserBase.Alt(
            parser,
            ParseTreeStub('a'),
            parserBase.Clauses(parser,
                ParseTreeStub('b'),
                parserBase.Alt(parser,
                    ParseTreeStub('c'),
                    ParseTreeStub('d'))))
        res = ast.Module(alt.topython())
        res = codegen.to_source(ast.Module(alt.topython()))
        self.assertEqual(res, ("try:\n"
                               "    try:\n"
                               "        if (not a):\n"
                               "            raise AltFalse()\n"
                               "        raise AltTrue()\n"
                               "    except AltFalse:\n"
                               "        pass\n"
                               "    try:\n"
                               "        if (not b):\n"
                               "            raise AltFalse()\n"
                               "        try:\n"
                               "            try:\n"
                               "                if (not c):\n"
                               "                    raise AltFalse()\n"
                               "                raise AltTrue()\n"
                               "            except AltFalse:\n"
                               "                pass\n"
                               "            try:\n"
                               "                if (not d):\n"
                               "                    raise AltFalse()\n"
                               "                raise AltTrue()\n"
                               "            except AltFalse:\n"
                               "                pass\n"
                               "            raise AltFalse()\n"
                               "        except AltTrue:\n"
                               "            pass\n"
                               "        raise AltTrue()\n"
                               "    except AltFalse:\n"
                               "        pass\n"
                               "    return False\n"
                               "except AltTrue:\n"
                               "    pass"))
###

    def test_topython_generates_code_for_repoptional(self):
        parser = None
        rep = parserBase.RepOptional(parser, ParseTreeStub('a'))
        res = codegen.to_source(rep.topython())
        self.assertEqual(res, "lambda : (a or True)")

    def test_topython_generates_code_for_rep0n(self):
        parser = None
        rep = parserBase.Rep0N(parser, ParseTreeStub('a'))
        ast_ = ast.Module(rep.topython())
        res = codegen.to_source(ast_)
        self.assertEqual(res,
            ("while True:\n"
             "    if (not a):\n"
             "        break"))

    def test_topython_generates_code_for_rep1n(self):
        parser = None
        rep = parserBase.Rep1N(parser, ParseTreeStub('a'))
        res = codegen.to_source(ast.Module(rep.topython()))
        self.assertEqual(res,
            ("if (not a):\n"
             "    return False\n"
             "while True:\n"
             "    if (not a):\n"
             "        break"))

#    def test_topython_generates_code_for_capture(self):
#    def test_topython_generates_code_for_scope(self):

#TODO(bps): remove till end of file
    def help(self, rule):
        res = rule.topython()
        if isinstance(res, list):
            res = ast.Module(res)
        code = codegen.to_source(res)
        return '\n'.join([
            "========== AST ==========",
            rule.dumpParseTree(),
            "========== CODE==========",
            code, 
            "========== END =========="])

    def test_topython_generates_code_for_parserdsl(self):
        from pyrser.dsl_parser.parserDsl import ParserDsl
        import pyrser.passes.dumpParseTree

        res, parser = '', ParserDsl()
        res = self.help(parser._ParserBase__rules['clause'])
        res = codegen.to_source(parser.rule_topython('bnf_dsl'))
        res = codegen.to_source(parser.rule_topython('rule'))
        res = codegen.to_source(parser.rule_topython('alternatives'))
        res = codegen.to_source(parser.rule_topython('clauses'))
        res = codegen.to_source(parser.rule_topython('clause'))
        res = codegen.to_source(parser.rule_topython('rule_name'))
        #print(res)
