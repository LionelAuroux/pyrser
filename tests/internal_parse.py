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
from pyrser.parsing.python.parserBase import *
from pyrser.passes.dumpParseTree import *

class InternalParse_Test(unittest.TestCase):
    @classmethod
    def setUpClass(cInternalParseClass):
        cInternalParseClass.oParse = ParserBase

    def test_01_readIdentifier(self):
        """
            Basic test for identifier parsing
        """
        oParse = InternalParse_Test.oParse()
        oParse.parsedStream("ceci est un test", sName = "root")
        self.assertTrue(
            oParse.beginTag('sujet') and oParse.readIdentifier() and oParse.endTag('sujet'),
            'failed in readIdentifier for sujet')
        sujet = oParse.getTag('sujet')
        oParse.skipIgnore()
        self.assertEqual(sujet, "ceci", "failed in capture sujet")
        self.assertTrue(
            oParse.beginTag('verbe') and oParse.readIdentifier() and oParse.endTag('verbe'),
            'failed in readIdentifier for verbe')
        verbe = oParse.getTag('verbe')
        oParse.skipIgnore()
        self.assertEqual(verbe, "est", "failed in capture verbe")
        self.assertTrue(
            oParse.beginTag('other') and oParse.readUntilEOF() and oParse.endTag('other'),
            'failed in readIdentifier for other')
        reste = oParse.getTag('other')
        self.assertEqual(reste, "un test", "failed in capture other")

    def test_02_readInteger(self):
        """
            Basic test for integer parsing
        """
        oParse = InternalParse_Test.oParse()
        oParse.parsedStream("12 333 44444444444444444444444444", sName = "root")
        self.assertTrue(
            oParse.beginTag('n1') and oParse.readInteger() and oParse.endTag('n1'),
            'failed in readInteger for n1')
        n1 = oParse.getTag('n1')
        oParse.skipIgnore()
        self.assertEqual(n1, "12", "failed in capture n1")
        self.assertTrue(
            oParse.beginTag('n2') and oParse.readInteger() and oParse.endTag('n2'),
            'failed in readInteger for n2')
        n2 = oParse.getTag('n2')
        oParse.skipIgnore()
        self.assertEqual(n2, "333", "failed in capture n2")
        self.assertTrue(
            oParse.beginTag('n3') and oParse.readInteger() and oParse.endTag('n3'),
            'failed in readInteger for n3')
        n3 = oParse.getTag('n3')
        self.assertEqual(n3, "44444444444444444444444444", "failed in capture n3")

    def test_03_linecol(self):
        """
            Basic test for line/col calculation
        """
        oParse = InternalParse_Test.oParse()
        oParse.parsedStream("X\nXX\nXXX\n")
        line = oParse.lineNbr
        col = oParse.columnNbr
        self.assertTrue(line == 1 and col == 1, "failed line/col at beginning")
        oParse.incPos()
        oParse.incPos()
        line = oParse.lineNbr
        col = oParse.columnNbr
        self.assertTrue(line == 2 and col == 1, "failed line/col at second")
        oParse.incPos()
        oParse.incPos()
        oParse.incPos()
        line = oParse.lineNbr
        col = oParse.columnNbr
        self.assertTrue(line == 3 and col == 1, "failed line/col at third")
        oParse.incPos()
        oParse.incPos()
        col = oParse.columnNbr
        self.assertTrue(line == 3 and col == 3, "failed line/col at col")
        oParse.incPos()
        oParse.incPos()
        line = oParse.lineNbr
        col = oParse.columnNbr
        self.assertTrue(line == 4 and col == 1, "failed line/col at forth")

    def test_04_readCChar(self):
        """
            Basic test for readCChar
        """
        oParse = InternalParse_Test.oParse()
        oParse.parsedStream("'c' '\\t'", sName = "root")
        self.assertTrue(
            oParse.beginTag('c1') and oParse.readCChar() and oParse.endTag('c1'),
            'failed in readCChar for c1')
        c1 = oParse.getTag('c1')
        oParse.skipIgnore()
        self.assertEqual(c1, "'c'", "failed in capture c1")
        self.assertTrue(
            oParse.beginTag('c2') and oParse.readCChar() and oParse.endTag('c2'),
            'failed in readCChar for c2')
        c2 = oParse.getTag('c2')
        self.assertEqual(c2, "'\\t'", "failed in capture c2")

    def test_05_readCString(self):
        """
            Basic test for readCString
        """
        oParse = InternalParse_Test.oParse()
        oParse.parsedStream('"premiere chaine" "deuxieme chaine\\n" "troisieme chainee \\"."', sName = "root")
        self.assertTrue(
            oParse.beginTag('s1') and oParse.readCString() and oParse.endTag('s1'),
            'failed in readCString for s1')
        s1 = oParse.getTag('s1')
        oParse.skipIgnore()
        self.assertEqual(s1, '"premiere chaine"', "failed in capture s1")
        self.assertTrue(
            oParse.beginTag('s2') and oParse.readCString() and oParse.endTag('s2'),
            'failed in readCString for s2')
        s2 = oParse.getTag('s2')
        oParse.skipIgnore()
        self.assertEqual(s2, '"deuxieme chaine\\n"', "failed in capture s2")
        self.assertTrue(
            oParse.beginTag('s3') and oParse.readCString() and oParse.endTag('s3'),
            'failed in readCString for s3')
        s3 = oParse.getTag('s3')
        self.assertEqual(s3, '"troisieme chainee \\"."', "failed in capture s3")

    def test_06_CallAndClauses(self):
        """
            Basic test for call/clauses
        """
        oParse = InternalParse_Test.oParse()
        oParse.parsedStream("abc def ghg")
        parseTree = Clauses(oParse,
            Call(oParse.beginTag, 'i1'), oParse.readIdentifier, Call(oParse.endTag, 'i1'),
            Call(oParse.beginTag, 'i2'), oParse.readIdentifier, Call(oParse.endTag, 'i2'),
            Call(oParse.beginTag, 'i3'), oParse.readIdentifier, Call(oParse.endTag, 'i3'),
        )
        parseTree()
        # Warning! skipIgnore is called between each Clauses
        self.assertEqual(oParse.getTag("i1"), "abc ", "failed in captured i1")
        self.assertEqual(oParse.getTag("i2"), "def ", "failed in captured i2")
        self.assertEqual(oParse.getTag("i3"), "ghg", "failed in captured i3")

    def test_07_RepXN(self):
        """
            Basic test for repeater
        """
        oParse = InternalParse_Test.oParse()
        oParse.parsedStream("12343 91219****1323 23")
        parseTree = Clauses(oParse,
            Call(oParse.beginTag, 'i1'), oParse.readInteger, Call(oParse.endTag, 'i1'),
            Rep0N(oParse, Call(oParse.readChar, '*')),
            Call(oParse.beginTag, 'i2'), 
                Rep1N(oParse, Call(oParse.readRange, '0', '9')),
            Call(oParse.endTag, 'i2'),
            Rep0N(oParse, Call(oParse.readChar, '*')),
            Call(oParse.beginTag, 'i3'), oParse.readInteger, Call(oParse.endTag, 'i3'),
            Call(oParse.readEOF)
        )
        parseTree()
        # Warning! skipIgnore is called between each Clauses
        self.assertEqual(oParse.getTag("i1"), "12343 ", "failed in captured i1")
        self.assertEqual(oParse.getTag("i2"), "91219", "failed in captured i2")
        self.assertEqual(oParse.getTag("i3"), "1323 ", "failed in captured i3")

    def test_08_RepAlt(self):
        """
            Basic test for alternatives
        """
        oParse = InternalParse_Test.oParse()
        oParse.parsedStream("_ad121dwdw ()[]")
        parseTree = Clauses(oParse,
            Call(oParse.beginTag, 'w1'), 
            Scope(oParse,
                begin = Call(oParse.pushIgnore, oParse.ignoreNull),
                end = Call(oParse.popIgnore),
                clause = Clauses(oParse,
                    Alt(oParse,
                        Call(oParse.readChar, '_'),
                        Call(oParse.readRange, 'a', 'z'),
                        Call(oParse.readRange, 'A', 'Z')
                    ),
                    Rep0N(oParse,
                        Alt(oParse,
                            Call(oParse.readChar, '_'),
                            Call(oParse.readRange, 'a', 'z'),
                            Call(oParse.readRange, 'A', 'Z'),
                            Call(oParse.readRange, '0', '9')
                        )
                    )
                )
            ),
            Call(oParse.endTag, 'w1'),
            Capture(oParse, 'w2',
                Rep1N(oParse,
                    Alt(oParse,
                        Call(oParse.readChar, '('),
                        Call(oParse.readChar, ')'),
                        Call(oParse.readChar, '['),
                        Call(oParse.readChar, ']'),
                    )
                )),
            Call(oParse.readEOF)
        )
        print("\n" + parseTree.dumpParseTree())
        parseTree()
        # Warning! skipIgnore is called between each Clauses
        self.assertEqual(oParse.getTag("w1"), "_ad121dwdw ", "failed in captured w1")
        self.assertEqual(oParse.getTag("w2"), "()[]", "failed in captured w2")
    
    def test_09_RepRules(self):
        """
            Basic test for Rules
        """
        @add_method(ParserBase)
        def printWord(self, test, tutu):
            test.assertEqual(tutu.value, "asbga", "failed access captured variable string")
        @add_method(ParserBase)
        def printint(self, test, toto):
            test.assertEqual(toto.value, "12121", "failed access captured variable int")
        oParse = InternalParse_Test.oParse()
        oParse.parsedStream("asbga    12121      njnj 89898")
        oParse.ruleNodes[-1]['test'] = self
        oParse.setHooks({'printWord' : oParse.printWord, 'printint' : oParse.printint})
        oParse.setRules({
            'main' : Rep0N(oParse, 
                        Alt(oParse, 
                            Clauses(oParse, Capture(oParse, 'tutu', Rule(oParse, 'word')), Hook(oParse, 'printWord', [("test", Node), ("tutu", Node)])),
                            Rule(oParse, 'int')
                        )
                    ),
            'word' : Scope(oParse, Call(oParse.pushIgnore, oParse.ignoreNull), Call(oParse.popIgnore),
                            Rep1N(oParse,
                                Alt(oParse,
                                    Call(oParse.readRange, 'a', 'z'),
                                    Call(oParse.readRange, 'A', 'Z')
                                )
                            )
                    ),
            'int' : Clauses(oParse, 
                        Scope(oParse, Call(oParse.pushIgnore, oParse.ignoreNull), Call(oParse.popIgnore),
                            Capture(oParse, 'toto', Rep1N(oParse, Call(oParse.readRange, '0', '9')))
                        ), 
                        Hook(oParse, 'printint', [("test", Node), ("toto", Node)])
                    )
            })
        bRes = oParse.evalRule('main')
        self.assertTrue(bRes, "failed to parse")

    def test_10_contextVariables(self):
        """
        Basic test for context variables
        """
        oParse = InternalParse_Test.oParse()
        oParse.ruleNodes[-1].update({'coucou':42, 'toto':[12, 33]})
        self.assertEqual(oParse.ruleNodes[-1]['toto'], [12, 33], "failed comparing list")
        #print("ruleNodes:%s" % oParse.ruleNodes)
        oParse.pushRuleNodes()
        oParse.ruleNodes[-1].update({'local1':666, 'local2':777})
        oParse.ruleNodes[-1]['toto'] = [1, 2, 3, 4]
        self.assertEqual(oParse.ruleNodes[-1]['coucou'], 42, "failed outer scope not visible in local")
        #print("ruleNodes:%s" % oParse.ruleNodes)
        oParse.popRuleNodes()

    def test_11_namespaceRules(self):
        """
        Test the namespace handling
        """
        oParse = InternalParse_Test.oParse()
        @add_method(ParserBase)
        def dummy(self):
            res = Node()
            res.text = "cool"
            self.ruleNodes[-1]["test"] = res
            return res
        oParse.setOneRule("A::B::C::test", Call(oParse.dummy))
        bRes = oParse.evalRule('test')
        self.assertEqual(bRes.text, "cool", "failed rule node in global namespace")
        bRes = oParse.evalRule('C::test')
        self.assertEqual(bRes.text, "cool", "failed rule node in global namespace")
        bRes = oParse.evalRule('B::C::test')
        self.assertEqual(bRes.text, "cool", "failed rule node in global namespace")
        bRes = oParse.evalRule('A::B::C::test')
        self.assertEqual(bRes.text, "cool", "failed rule node in global namespace")

    def test_12_defaultRules(self):
        """
        Test the presence of default rules
        """
        oParse = InternalParse_Test.oParse()
        self.assertTrue("num" in oParse.rules, "failed no found Base::num")
        self.assertTrue("Base::num" in oParse.rules, "failed no found Base::num")
        self.assertTrue("string" in oParse.rules, "failed no found Base::string")
        self.assertTrue("Base::string" in oParse.rules, "failed no found Base::string")

