# Copyright (C) 2013 Lionel Auroux
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
from pyrser.dsl_parser.parserDsl import *

class InternalDsl_Test(unittest.TestCase):
    @classmethod
    def setUpClass(cInternalParseClass):
        cInternalParseClass.oParse = ParserDsl

    def test_01_one_rule(self):
        """
        Test default
        """
        bnf = InternalDsl_Test.oParse("""
            the_rule ::= a
            ;
        """)
        res = bnf.evalRule('bnf_dsl')
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertTrue(isinstance(res['the_rule'], Rule), "failed in ParserTree type for node Rule")
        self.assertTrue(res['the_rule'].name == "a", "failed in ParserTree type for node Rule")

    def test_02_two_rules(self):
        """
        Test default
        """
        bnf = InternalDsl_Test.oParse("""
            the_rule ::= a b
            ;
        """)
        res = bnf.evalRule('bnf_dsl')
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertTrue(isinstance(res['the_rule'], Clauses), "failed in ParserTree type for node Clauses")
        self.assertTrue(isinstance(res['the_rule'].clauses[0], Rule), "failed in ParserTree type for node Rule")
        self.assertTrue(res['the_rule'].clauses[0].name == "a", "failed in name of rule 'a'")
        self.assertTrue(isinstance(res['the_rule'].clauses[1], Rule), "failed in ParserTree type for node Rule")
        self.assertTrue(res['the_rule'].clauses[1].name == "b", "failed in name of rule 'b'")

    def test_03_more_rules(self):
        """
        Test default
        """
        bnf = InternalDsl_Test.oParse("""
            the_rule ::= a b c
            ;
        """)
        res = bnf.evalRule('bnf_dsl')
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertTrue(isinstance(res['the_rule'], Clauses), "failed in ParserTree type for node Clauses")
        self.assertTrue(isinstance(res['the_rule'].clauses[0], Rule), "failed in ParserTree type for node Rule")
        self.assertTrue(res['the_rule'].clauses[0].name == "a", "failed in name of rule 'a'")
        self.assertTrue(isinstance(res['the_rule'].clauses[1], Rule), "failed in ParserTree type for node Rule")
        self.assertTrue(res['the_rule'].clauses[1].name == "b", "failed in name of rule 'b'")
        self.assertTrue(isinstance(res['the_rule'].clauses[2], Rule), "failed in ParserTree type for node Rule")
        self.assertTrue(res['the_rule'].clauses[2].name == "c", "failed in name of rule 'c'")

    def test_04_one_alt(self):
        """
        Test default
        """
        bnf = InternalDsl_Test.oParse("""
            the_rule ::= a | b
            ;
        """)
        res = bnf.evalRule('bnf_dsl')
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertTrue(isinstance(res['the_rule'], Alt), "failed in ParserTree type for node Alt")
        self.assertTrue(isinstance(res['the_rule'].clauses[0], Rule), "failed in ParserTree type for node Rule")
        self.assertTrue(res['the_rule'].clauses[0].name == "a", "failed in name of rule 'a'")
        self.assertTrue(isinstance(res['the_rule'].clauses[1], Rule), "failed in ParserTree type for node Rule")
        self.assertTrue(res['the_rule'].clauses[1].name == "b", "failed in name of rule 'b'")

    def test_05_two_alt(self):
        """
        Test default
        """
        bnf = InternalDsl_Test.oParse("""
            the_rule ::= a | b | c
            ;
        """)
        res = bnf.evalRule('bnf_dsl')
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertTrue(isinstance(res['the_rule'], Alt), "failed in ParserTree type for node Alt")
        self.assertTrue(isinstance(res['the_rule'].clauses[0], Rule), "failed in ParserTree type for node Rule")
        self.assertTrue(res['the_rule'].clauses[0].name == "a", "failed in name of rule 'a'")
        self.assertTrue(isinstance(res['the_rule'].clauses[1], Rule), "failed in ParserTree type for node Rule")
        self.assertTrue(res['the_rule'].clauses[1].name == "b", "failed in name of rule 'b'")
        self.assertTrue(isinstance(res['the_rule'].clauses[2], Rule), "failed in ParserTree type for node Rule")
        self.assertTrue(res['the_rule'].clauses[2].name == "c", "failed in name of rule 'c'")

    def test_06_char(self):
        """
        Test default
        """
        bnf = InternalDsl_Test.oParse("""
            the_rule ::= 'a'
            ;
        """)
        res = bnf.evalRule('bnf_dsl')
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertTrue(isinstance(res['the_rule'], Call), "failed in ParserTree type for node Call")
        self.assertTrue(res['the_rule'].callObject.__name__ == ParserBase.readChar.__name__, "failed in ParserTree type for call to readChar")
        self.assertTrue(res['the_rule'].params[0] == 'a', "failed in ParserTree type for param[0] to 'a'")

    def test_07_string(self):
        """
        Test default
        """
        bnf = InternalDsl_Test.oParse("""
            the_rule ::= "bonjour le monde"
            ;
        """)
        res = bnf.evalRule('bnf_dsl')
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertTrue(isinstance(res['the_rule'], Call), "failed in ParserTree type for node Call")
        self.assertTrue(res['the_rule'].callObject.__name__ == ParserBase.readText.__name__, "failed in ParserTree type for call to readText")
        self.assertTrue(res['the_rule'].params[0] == "bonjour le monde", 'failed in ParserTree type for param[0] to "bonjour le monde"')

    def test_08_range(self):
        """
        Test default
        """
        bnf = InternalDsl_Test.oParse("""
            the_rule ::= 'a'..'z'
            ;
        """)
        res = bnf.evalRule('bnf_dsl')
        self.assertTrue('the_rule' in res, "failed to fetch the rule name")
        self.assertTrue(isinstance(res['the_rule'], Call), "failed in ParserTree type for node Call")
        self.assertTrue(res['the_rule'].callObject.__name__ == ParserBase.readRange.__name__, "failed in ParserTree type for call to readRange")
        self.assertTrue(res['the_rule'].params[0] == 'a', "failed in ParserTree type for param[0] to 'a'")
        self.assertTrue(res['the_rule'].params[1] == 'z', "failed in ParserTree type for param[1] to 'z'")
