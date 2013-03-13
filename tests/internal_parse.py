import unittest

from pyrser import meta
from pyrser import node
from pyrser import parsing
from pyrser.passes import dumpParseTree


class InternalParse_Test(unittest.TestCase):
    def test_01_readIdentifier(self):
        """
            Basic test for identifier parsing
        """
        parser = parsing.Parser()
        parser.parsedStream("ceci est un test", sName="root")
        self.assertTrue(
            parser.beginTag('sujet') and
            parser.readIdentifier() and
            parser.endTag('sujet'),
            'failed in readIdentifier for sujet')
        sujet = parser.getTag('sujet')
        parser.skipIgnore()
        self.assertEqual(sujet, "ceci", "failed in capture sujet")
        self.assertTrue(
            parser.beginTag('verbe') and
            parser.readIdentifier() and
            parser.endTag('verbe'),
            'failed in readIdentifier for verbe')
        verbe = parser.getTag('verbe')
        parser.skipIgnore()
        self.assertEqual(verbe, "est", "failed in capture verbe")
        self.assertTrue(
            parser.beginTag('other') and
            parser.readUntilEOF() and
            parser.endTag('other'),
            'failed in readIdentifier for other')
        reste = parser.getTag('other')
        self.assertEqual(reste, "un test", "failed in capture other")

    def test_02_readInteger(self):
        """
            Basic test for integer parsing
        """
        parser = parsing.Parser()
        parser.parsedStream("12 333 44444444444444444444444444", sName="root")
        self.assertTrue(
            parser.beginTag('n1') and
            parser.readInteger() and
            parser.endTag('n1'),
            'failed in readInteger for n1')
        n1 = parser.getTag('n1')
        parser.skipIgnore()
        self.assertEqual(n1, "12", "failed in capture n1")
        self.assertTrue(
            parser.beginTag('n2') and
            parser.readInteger() and
            parser.endTag('n2'),
            'failed in readInteger for n2')
        n2 = parser.getTag('n2')
        parser.skipIgnore()
        self.assertEqual(n2, "333", "failed in capture n2")
        self.assertTrue(
            parser.beginTag('n3') and
            parser.readInteger() and
            parser.endTag('n3'),
            'failed in readInteger for n3')
        n3 = parser.getTag('n3')
        self.assertEqual(n3, "44444444444444444444444444",
                         "failed in capture n3")

    def test_04_readCChar(self):
        """
            Basic test for readCChar
        """
        parser = parsing.Parser()
        parser.parsedStream(r"'c' '\t'", sName="root")
        self.assertTrue(
            parser.beginTag('c1') and
            parser.readCChar() and
            parser.endTag('c1'),
            'failed in readCChar for c1')
        c1 = parser.getTag('c1')
        parser.skipIgnore()
        self.assertEqual(c1, "'c'", "failed in capture c1")
        self.assertTrue(
            parser.beginTag('c2') and
            parser.readCChar() and
            parser.endTag('c2'),
            'failed in readCChar for c2')
        c2 = parser.getTag('c2')
        self.assertEqual(c2, r"'\t'", "failed in capture c2")

    def test_05_readCString(self):
        """
            Basic test for readCString
        """
        parser = parsing.Parser()
        parser.parsedStream(
            r'"premiere chaine"'
            r'"deuxieme chaine\n"'
            r'"troisieme chainee \"."',
            sName="root")
        self.assertTrue(
            parser.beginTag('s1') and
            parser.readCString() and
            parser.endTag('s1'),
            'failed in readCString for s1')
        s1 = parser.getTag('s1')
        parser.skipIgnore()
        self.assertEqual(s1, '"premiere chaine"', "failed in capture s1")
        self.assertTrue(
            parser.beginTag('s2') and
            parser.readCString() and
            parser.endTag('s2'),
            'failed in readCString for s2')
        s2 = parser.getTag('s2')
        parser.skipIgnore()
        self.assertEqual(s2, '"deuxieme chaine\\n"', "failed in capture s2")
        self.assertTrue(
            parser.beginTag('s3') and
            parser.readCString() and
            parser.endTag('s3'),
            'failed in readCString for s3')
        s3 = parser.getTag('s3')
        self.assertEqual(s3, r'"troisieme chainee \"."',
                         "failed in capture s3")

    def test_06_CallAndClauses(self):
        """
            Basic test for call/clauses
        """
        parser = parsing.Parser()
        parser.parsedStream("abc def ghg")
        parseTree = parsing.Clauses(
            parsing.Call(parser.beginTag, 'i1'),
            parsing.Parser.readIdentifier,
            parsing.Call(parser.endTag, 'i1'),
            parsing.Call(parser.beginTag, 'i2'),
            parsing.Parser.readIdentifier,
            parsing.Call(parser.endTag, 'i2'),
            parsing.Call(parser.beginTag, 'i3'),
            parsing.Parser.readIdentifier,
            parsing.Call(parser.endTag, 'i3'))
        parseTree(parser)
        # Warning! skipIgnore is called between each parsing.Clauses
        self.assertEqual(parser.getTag("i1"), "abc ", "failed in captured i1")
        self.assertEqual(parser.getTag("i2"), "def ", "failed in captured i2")
        self.assertEqual(parser.getTag("i3"), "ghg", "failed in captured i3")

    def test_07_RepXN(self):
        """
            Basic test for repeater
        """
        parser = parsing.Parser()
        parser.parsedStream("12343 91219****1323 23")
        parseTree = parsing.Clauses(
            parsing.Call(parser.beginTag, 'i1'),
            parsing.Parser.readInteger,
            parsing.Call(parser.endTag, 'i1'),
            parsing.Rep0N(parsing.Call(parser.readChar, '*')),
            parsing.Call(parser.beginTag, 'i2'),
            parsing.Rep1N(parsing.Call(parser.readRange, '0', '9')),
            parsing.Call(parser.endTag, 'i2'),
            parsing.Rep0N(parsing.Call(parser.readChar, '*')),
            parsing.Call(parser.beginTag, 'i3'),
            parsing.Parser.readInteger,
            parsing.Call(parser.endTag, 'i3'),
            parsing.Call(parser.readEOF))
        parseTree(parser)
        # Warning! skipIgnore is called between each parsing.Clauses
        self.assertEqual(parser.getTag("i1"), "12343 ",
                         "failed in captured i1")
        self.assertEqual(parser.getTag("i2"), "91219",
                         "failed in captured i2")
        self.assertEqual(parser.getTag("i3"), "1323 ",
                         "failed in captured i3")

    def test_08_RepAlt(self):
        """
            Basic test for alternatives
        """
        parser = parsing.Parser()
        parser.parsedStream("_ad121dwdw ()[]")
        parseTree = parsing.Clauses(
            parsing.Call(parser.beginTag, 'w1'),
            parsing.Scope(
                begin=parsing.Call(parser.pushIgnore, parser.ignoreNull),
                end=parsing.Call(parser.popIgnore),
                clause=parsing.Clauses(
                    parsing.Alt(
                        parsing.Call(parser.readChar, '_'),
                        parsing.Call(parser.readRange, 'a', 'z'),
                        parsing.Call(parser.readRange, 'A', 'Z')
                    ),
                    parsing.Rep0N(
                        parsing.Alt(
                            parsing.Call(parser.readChar, '_'),
                            parsing.Call(parser.readRange, 'a', 'z'),
                            parsing.Call(parser.readRange, 'A', 'Z'),
                            parsing.Call(parser.readRange, '0', '9'))))),
            parsing.Call(parser.endTag, 'w1'),
            parsing.Capture(
                'w2',
                parsing.Rep1N(
                    parsing.Alt(
                        parsing.Call(parser.readChar, '('),
                        parsing.Call(parser.readChar, ')'),
                        parsing.Call(parser.readChar, '['),
                        parsing.Call(parser.readChar, ']'),
                    )
                )),
            parsing.Call(parser.readEOF)
        )
        #print("\n" + parseTree.dumpParseTree())
        parseTree(parser)
        # Warning! skipIgnore is called between each parsing.Clauses
        self.assertEqual(parser.getTag("w1"), "_ad121dwdw ",
                         "failed in captured w1")
        self.assertEqual(parser.getTag("w2"), "()[]",
                         "failed in captured w2")

    def test_09_RepRules(self):
        """
            Basic test for Rules
        """
        def printWord(parser, test, tutu):
            test.assertEqual(tutu.value, "asbga",
                             "failed access captured variable string")

        def printint(parser, test, toto):
            #TODO(bps): printint should be called, delete raise when called
            raise Exception("Delete when called")
            test.assertEqual(toto.value, "12121",
                             "failed access captured variable int")

        parser = parsing.Parser()
        parser.parsedStream("asbga    12121      njnj 89898")
        parser.rulenodes[-1]['test'] = self
        parser.setHooks({'printWord': printWord,
                         'printint': printint})
        parser.setRules({
            'main': parsing.Rep0N(
                parsing.Alt(
                    parsing.Clauses(
                        parsing.Capture('tutu', parsing.Rule('word')),
                        parsing.Hook(
                            'printWord',
                            [("test", node.Node), ("tutu", node.Node)])),
                    parsing.Rule('int'))),
            'word': parsing.Scope(
                parsing.Call(parser.pushIgnore, parser.ignoreNull),
                parsing.Call(parser.popIgnore),
                parsing.Rep1N(
                    parsing.Alt(
                        parsing.Call(parser.readRange, 'a', 'z'),
                        parsing.Call(parser.readRange, 'A', 'Z')))),
            'int': parsing.Clauses(
                parsing.Scope(
                    parsing.Call(parser.pushIgnore, parser.ignoreNull),
                    parsing.Call(parser.popIgnore),
                    parsing.Capture(
                        'toto',
                        parsing.Rep1N(
                            parsing.Call(parser.readRange, '0', '9')))),
                parsing.Hook(
                    'printint',
                    [("test", node.Node), ("toto", node.Node)]))})
        bRes = parser.evalRule('main')
        self.assertTrue(bRes, "failed to parse")

    def test_10_contextVariables(self):
        """
        Basic test for context variables
        """
        parser = parsing.Parser()
        parser.rulenodes[-1].update({'coucou': 42, 'toto': [12, 33]})
        self.assertEqual(parser.rulenodes[-1]['toto'], [12, 33],
                         "failed comparing list")
        #print("rulenodes:%s" % parser.rulenodes)
        parser.pushRuleNodes()
        parser.rulenodes[-1].update({'local1': 666, 'local2': 777})
        parser.rulenodes[-1]['toto'] = [1, 2, 3, 4]
        self.assertEqual(parser.rulenodes[-1]['coucou'], 42,
                         "failed outer scope not visible in local")
        #print("rulenodes:%s" % parser.rulenodes)
        parser.popRuleNodes()

    def test_11_namespaceRules(self):
        """
        Test the namespace handling
        """
        parser = parsing.Parser()

        @meta.add_method(parsing.Parser)
        def dummy(self):
            res = node.Node()
            res.text = "cool"
            self.rulenodes[-1]["test"] = res
            return res
        parser.setOneRule("A::B::C::test", parsing.Call(parser.dummy))
        bRes = parser.evalRule('test')
        self.assertEqual(bRes.text, "cool",
                         "failed rule node in global namespace")
        bRes = parser.evalRule('C::test')
        self.assertEqual(bRes.text, "cool",
                         "failed rule node in global namespace")
        bRes = parser.evalRule('B::C::test')
        self.assertEqual(bRes.text, "cool",
                         "failed rule node in global namespace")
        bRes = parser.evalRule('A::B::C::test')
        self.assertEqual(bRes.text, "cool",
                         "failed rule node in global namespace")

    def test_12_defaultRules(self):
        """
        Test the presence of default rules
        """
        parser = parsing.Parser()
        self.assertTrue("num" in parser._rules, "failed no found Base::num")
        self.assertTrue("Base::num" in parser._rules,
                        "failed no found Base::num")
        self.assertTrue("string" in parser._rules,
                        "failed no found Base::string")
        self.assertTrue("Base::string" in parser._rules,
                        "failed no found Base::string")
