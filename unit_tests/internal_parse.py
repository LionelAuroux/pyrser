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
        self.assertEqual(sujet, "ceci", "failed in capture sujet")
        self.assertTrue(
            oParse.beginTag('verbe') and oParse.readIdentifier() and oParse.endTag('verbe'),
            'failed in readIdentifier for verbe')
        verbe = oParse.getTag('verbe')
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
        self.assertEqual(n1, "12", "failed in capture n1")
        self.assertTrue(
            oParse.beginTag('n2') and oParse.readInteger() and oParse.endTag('n2'),
            'failed in readInteger for n2')
        n2 = oParse.getTag('n2')
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
        self.assertEqual(s1, '"premiere chaine"', "failed in capture s1")
        self.assertTrue(
            oParse.beginTag('s2') and oParse.readCString() and oParse.endTag('s2'),
            'failed in readCString for s2')
        s2 = oParse.getTag('s2')
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
        parseTree = Clauses(\
            Call(oParse.beginTag, 'i1'), oParse.readIdentifier, Call(oParse.endTag, 'i1'),
            Call(oParse.beginTag, 'i2'), oParse.readIdentifier, Call(oParse.endTag, 'i2'),
            Call(oParse.beginTag, 'i3'), oParse.readIdentifier, Call(oParse.endTag, 'i3'),
        )
        parseTree()
        self.assertEqual(oParse.getTag("i1"), "abc", "failed in captured i1")
        self.assertEqual(oParse.getTag("i2"), "def", "failed in captured i2")
        self.assertEqual(oParse.getTag("i3"), "ghg", "failed in captured i3")

    def test_07_RepXN(self):
        """
            Basic test for repeater
        """
        oParse = InternalParse_Test.oParse()
        oParse.parsedStream("12343 91219****1323 23")
        parseTree = Clauses(\
            Call(oParse.beginTag, 'i1'), oParse.readInteger, Call(oParse.endTag, 'i1'),
            Rep0N(Call(oParse.readChar, '*')),
            Call(oParse.beginTag, 'i2'), 
                Rep1N(Call(oParse.readRange, '0', '9')),
            Call(oParse.endTag, 'i2'),
            Rep0N(Call(oParse.readChar, '*')),
            Call(oParse.beginTag, 'i3'), oParse.readInteger, Call(oParse.endTag, 'i3'),
            Call(oParse.readEOF)
        )
        parseTree()
        self.assertEqual(oParse.getTag("i1"), "12343", "failed in captured i1")
        self.assertEqual(oParse.getTag("i2"), "91219", "failed in captured i2")
        self.assertEqual(oParse.getTag("i3"), "1323", "failed in captured i3")

    def test_08_RepAlt(self):
        """
            Basic test for alternatives
        """
        oParse = InternalParse_Test.oParse()
        oParse.parsedStream("_ad121dwdw ()[]")
        parseTree = Clauses(\
            Call(oParse.beginTag, 'w1'), 
            Scope(
                begin = Call(oParse.pushIgnore, oParse.ignoreNull),
                end = Call(oParse.popIgnore),
                clause = Clauses(
                    Alt(\
                        Call(oParse.readChar, '_'),
                        Call(oParse.readRange, 'a', 'z'),
                        Call(oParse.readRange, 'A', 'Z')
                    ),
                    Rep0N(\
                        Alt(\
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
                Rep1N(\
                    Alt(\
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
        self.assertEqual(oParse.getTag("w1"), "_ad121dwdw", "failed in captured w1")
        self.assertEqual(oParse.getTag("w2"), "()[]", "failed in captured w2")
    
    def test_09_RepRules(self):
        """
            Basic test for Rules
        """
        def printWord(parser, ctx):
            print("CTX:<%s><%s>" % (ctx, ctx['tutu']))
        def printint(parser, ctx):
            print("CTX:<%s><%s>" % (ctx, ctx['toto']))
        oParse = InternalParse_Test.oParse()
        oParse.parsedStream("asbga    12121      njnj 89898")
        oParse.setHooks({'printWord' : printWord})
        oParse.setRules({
            'main' : Rep0N(Alt(Clauses(Rule(oParse, 'word'), Hook(oParse, 'printWord')), Rule(oParse, 'int'))),
            'word' : Scope(Call(oParse.pushIgnore, oParse.ignoreNull), Call(oParse.popIgnore),
                        Capture(oParse, 'tutu', Rep1N(\
                            Alt(\
                                Call(oParse.readRange, 'a', 'z'),
                                Call(oParse.readRange, 'A', 'Z')
                            )
                        ))),
            'int' : Clauses(Scope(Call(oParse.pushIgnore, oParse.ignoreNull), Call(oParse.popIgnore),
                        Capture(oParse, 'toto', Rep1N(Call(oParse.readRange, '0', '9')))
                        ), Hook(oParse, 'printint'))
            })
        bRes = oParse.evalRule('main')

    def test_10_contextVariables(self):
        """
        Basic test for context variables
        """
        pass
