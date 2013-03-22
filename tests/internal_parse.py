import unittest
try:
    from unittest import mock
except ImportError:
    import mock

from pyrser import meta
from pyrser import parsing
import pyrser.passes.dumpParseTree


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

    def test_06_CallAndSeq(self):
        """
            Basic test for call/clauses
        """
        parser = parsing.Parser()
        parser.parsedStream("abc def ghg")
        parseTree = parsing.Seq(
            parsing.Call(parsing.Parser.beginTag, 'i1'),
            parsing.Parser.readIdentifier,
            parsing.Call(parsing.Parser.endTag, 'i1'),
            parsing.Call(parsing.Parser.beginTag, 'i2'),
            parsing.Parser.readIdentifier,
            parsing.Call(parsing.Parser.endTag, 'i2'),
            parsing.Call(parsing.Parser.beginTag, 'i3'),
            parsing.Parser.readIdentifier,
            parsing.Call(parsing.Parser.endTag, 'i3'))
        parseTree(parser)
        # Warning! skipIgnore is called between each parsing.Seq
        self.assertEqual(parser.getTag("i1"), "abc ", "failed in captured i1")
        self.assertEqual(parser.getTag("i2"), "def ", "failed in captured i2")
        self.assertEqual(parser.getTag("i3"), "ghg", "failed in captured i3")

    def test_07_RepXN(self):
        """
            Basic test for repeater
        """
        parser = parsing.Parser()
        parser.parsedStream("12343 91219****1323 23")
        parseTree = parsing.Seq(
            parsing.Call(parsing.Parser.beginTag, 'i1'),
            parsing.Parser.readInteger,
            parsing.Call(parsing.Parser.endTag, 'i1'),
            parsing.Rep0N(parsing.Call(parsing.Parser.readChar, '*')),
            parsing.Call(parsing.Parser.beginTag, 'i2'),
            parsing.Rep1N(parsing.Call(parsing.Parser.readRange, '0', '9')),
            parsing.Call(parsing.Parser.endTag, 'i2'),
            parsing.Rep0N(parsing.Call(parsing.Parser.readChar, '*')),
            parsing.Call(parsing.Parser.beginTag, 'i3'),
            parsing.Parser.readInteger,
            parsing.Call(parsing.Parser.endTag, 'i3'),
            parsing.Call(parsing.Parser.readEOF))
        parseTree(parser)
        # Warning! skipIgnore is called between each parsing.Seq
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
        parseTree = parsing.Seq(
            parsing.Call(parsing.Parser.beginTag, 'w1'),
            parsing.Scope(
                begin=parsing.Call(parsing.Parser.pushIgnore,
                                   parsing.Parser.ignore_null),
                end=parsing.Call(parsing.Parser.popIgnore),
                pt=parsing.Seq(
                    parsing.Alt(
                        parsing.Call(parsing.Parser.readChar, '_'),
                        parsing.Call(parsing.Parser.readRange, 'a', 'z'),
                        parsing.Call(parsing.Parser.readRange, 'A', 'Z')
                    ),
                    parsing.Rep0N(
                        parsing.Alt(
                            parsing.Call(parsing.Parser.readChar, '_'),
                            parsing.Call(parsing.Parser.readRange, 'a', 'z'),
                            parsing.Call(parsing.Parser.readRange, 'A', 'Z'),
                            parsing.Call(parsing.Parser.readRange,
                                         '0', '9'))))),
            parsing.Call(parsing.Parser.endTag, 'w1'),
            parsing.Capture(
                'w2',
                parsing.Rep1N(
                    parsing.Alt(
                        parsing.Call(parsing.Parser.readChar, '('),
                        parsing.Call(parsing.Parser.readChar, ')'),
                        parsing.Call(parsing.Parser.readChar, '['),
                        parsing.Call(parsing.Parser.readChar, ']'),
                    )
                )),
            parsing.Call(parsing.Parser.readEOF)
        )
        parseTree.dumpParseTree()
        parseTree(parser)
        # Warning! skipIgnore is called between each parsing.Seq
        self.assertEqual(parser.getTag("w1"), "_ad121dwdw ",
                         "failed in captured w1")
        self.assertEqual(parser.getTag("w2"), "()[]",
                         "failed in captured w2")

    def test_09_RepRules(self):
        """
            Basic test for Rules
        """
        def check_word(parser, test, tutu):
            test.assertIn(tutu.value, ('asbga', 'njnj'))
            return True

        def check_int(parser, test, toto):
            test.assertIn(toto.value, ('12121', '89898'))
            return True

        check_word = mock.Mock(side_effect=check_word)
        check_int = mock.Mock(side_effect=check_int)

        parser = parsing.Parser()
        parser.parsedStream("asbga    12121      njnj 89898")
        parser.rulenodes[-1]['test'] = self
        parser.setHooks({'checkWord': check_word, 'checkInt': check_int})
        parser.setRules({
            'main': parsing.Seq(
                parsing.Rep0N(
                    parsing.Alt(
                        parsing.Seq(
                            parsing.Capture('tutu', parsing.Rule('word')),
                            parsing.Hook(
                                'checkWord',
                                [("test", parsing.Node),
                                 ("tutu", parsing.Node)])),
                        parsing.Rule('int'))),
                parsing.Rule('Base.eof')),
            'word': parsing.Scope(
                parsing.Call(parsing.Parser.pushIgnore,
                             parsing.Parser.ignore_null),
                parsing.Call(parsing.Parser.popIgnore),
                parsing.Rep1N(
                    parsing.Alt(
                        parsing.Call(parsing.Parser.readRange, 'a', 'z'),
                        parsing.Call(parsing.Parser.readRange, 'A', 'Z')))),
            'int': parsing.Seq(
                parsing.Scope(
                    parsing.Call(parsing.Parser.pushIgnore,
                                 parsing.Parser.ignore_null),
                    parsing.Call(parsing.Parser.popIgnore),
                    parsing.Capture(
                        'toto',
                        parsing.Rep1N(
                            parsing.Call(parsing.Parser.readRange,
                                         '0', '9')))),
                parsing.Hook(
                    'checkInt',
                    [("test", parsing.Node), ("toto", parsing.Node)]))})
        bRes = parser.evalRule('main')
        self.assertTrue(bRes, "failed to parse")
        self.assertEqual(2, check_word.call_count)
        self.assertEqual(2, check_int.call_count)

    def test_10_contextVariables(self):
        """
        Basic test for context variables
        """
        parser = parsing.Parser()
        parser.rulenodes[-1].update({'coucou': 42, 'toto': [12, 33]})
        self.assertEqual(parser.rulenodes[-1]['toto'], [12, 33],
                         "failed comparing list")
        parser.pushRuleNodes()
        parser.rulenodes[-1].update({'local1': 666, 'local2': 777})
        parser.rulenodes[-1]['toto'] = [1, 2, 3, 4]
        self.assertEqual(parser.rulenodes[-1]['coucou'], 42,
                         "failed outer scope not visible in local")
        parser.popRuleNodes()

    def test_11_namespaceRules(self):
        """
        Test the namespace handling
        """
        parser = parsing.Parser()

        @meta.add_method(parsing.Parser)
        def dummy(self):
            res = parsing.Node()
            res.text = "cool"
            self.rulenodes[-1]["test"] = res
            return res
        parser.setOneRule("A.B.C.test", parsing.Call(parsing.Parser.dummy))
        bRes = parser.evalRule('test')
        self.assertEqual(bRes.text, "cool",
                         "failed rule node in global namespace")
        bRes = parser.evalRule('C.test')
        self.assertEqual(bRes.text, "cool",
                         "failed rule node in global namespace")
        bRes = parser.evalRule('B.C.test')
        self.assertEqual(bRes.text, "cool",
                         "failed rule node in global namespace")
        bRes = parser.evalRule('A.B.C.test')
        self.assertEqual(bRes.text, "cool",
                         "failed rule node in global namespace")

    def test_12_defaultRules(self):
        """
        Test the presence of default rules
        """
        parser = parsing.Parser()
        self.assertTrue("num" in parser._rules, "failed no found Base.num")
        self.assertTrue("Base.num" in parser._rules,
                        "failed no found Base.num")
        self.assertTrue("string" in parser._rules,
                        "failed no found Base.string")
        self.assertTrue("Base.string" in parser._rules,
                        "failed no found Base.string")

    def test_13_Directive(self):
        """Test Directive/DirectiveWrapper
        """
        class   DummyDirective(parsing.DirectiveWrapper):
            def begin(self, parser, a, b):
                print("BEGIN %s %s" % (a, b))
                return True
            def end(self, parser, a, b):
                print("END %s %s" % (a, b))
                return True
        def dummyParser(p):
            return True
        direct = parsing.Directive(DummyDirective(), [(1, int), (2, int)], dummyParser)
        direct(dummyParser)
