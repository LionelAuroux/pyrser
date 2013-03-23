import unittest
try:
    from unittest import mock
except ImportError:
    import mock

from pyrser import meta
from pyrser import parsing
from pyrser.parsing import MetaBasicParser
import pyrser.passes.dumpParseTree
import collections

class InternalParse_Test(unittest.TestCase):
    def test_00_Directive(self):
        """Test Directive/DirectiveWrapper
        """
        class   DummyDirective(parsing.DirectiveWrapper):
            def begin(self, test, a: int, b: int):
                test.assertTrue(a == 1, "failed to recv first parameter into DummyDirective.begin")
                test.assertTrue(b == 2, "failed to recv second parameter into DummyDirective.begin")
                return True
            def end(self, test, a: int, b: int):
                test.assertTrue(a == 1, "failed to recv first parameter into DummyDirective.end")
                test.assertTrue(b == 2, "failed to recv second parameter into DummyDirective.end")
                return True
        def dummyParser(p):
            return True
        direct = parsing.Directive(DummyDirective(), [(1, int), (2, int)], dummyParser)
        direct(self)

    def test_01_readIdentifier(self):
        """
            Basic test for identifier parsing
        """
        parser = parsing.Parser()
        parser.parsed_stream("ceci est un test", sName="root")
        self.assertTrue(
            parser.begin_tag('sujet') and
            parser.read_identifier() and
            parser.end_tag('sujet'),
            'failed in read_identifier for sujet')
        sujet = parser.get_tag('sujet')
        parser.skip_ignore()
        self.assertEqual(sujet, "ceci", "failed in capture sujet")
        self.assertTrue(
            parser.begin_tag('verbe') and
            parser.read_identifier() and
            parser.end_tag('verbe'),
            'failed in read_identifier for verbe')
        verbe = parser.get_tag('verbe')
        parser.skip_ignore()
        self.assertEqual(verbe, "est", "failed in capture verbe")
        self.assertTrue(
            parser.begin_tag('other') and
            parser.read_until_eof() and
            parser.end_tag('other'),
            'failed in read_identifier for other')
        reste = parser.get_tag('other')
        self.assertEqual(reste, "un test", "failed in capture other")

    def test_02_readInteger(self):
        """
            Basic test for integer parsing
        """
        parser = parsing.Parser()
        parser.parsed_stream("12 333 44444444444444444444444444", sName="root")
        self.assertTrue(
            parser.begin_tag('n1') and
            parser.read_integer() and
            parser.end_tag('n1'),
            'failed in read_integer for n1')
        n1 = parser.get_tag('n1')
        parser.skip_ignore()
        self.assertEqual(n1, "12", "failed in capture n1")
        self.assertTrue(
            parser.begin_tag('n2') and
            parser.read_integer() and
            parser.end_tag('n2'),
            'failed in read_integer for n2')
        n2 = parser.get_tag('n2')
        parser.skip_ignore()
        self.assertEqual(n2, "333", "failed in capture n2")
        self.assertTrue(
            parser.begin_tag('n3') and
            parser.read_integer() and
            parser.end_tag('n3'),
            'failed in read_integer for n3')
        n3 = parser.get_tag('n3')
        self.assertEqual(n3, "44444444444444444444444444",
                         "failed in capture n3")

    def test_04_readCChar(self):
        """
            Basic test for read_cchar
        """
        parser = parsing.Parser()
        parser.parsed_stream(r"'c' '\t'", sName="root")
        self.assertTrue(
            parser.begin_tag('c1') and
            parser.read_cchar() and
            parser.end_tag('c1'),
            'failed in read_cchar for c1')
        c1 = parser.get_tag('c1')
        parser.skip_ignore()
        self.assertEqual(c1, "'c'", "failed in capture c1")
        self.assertTrue(
            parser.begin_tag('c2') and
            parser.read_cchar() and
            parser.end_tag('c2'),
            'failed in read_cchar for c2')
        c2 = parser.get_tag('c2')
        self.assertEqual(c2, r"'\t'", "failed in capture c2")

    def test_05_readCString(self):
        """
            Basic test for read_cstring
        """
        parser = parsing.Parser()
        parser.parsed_stream(
            r'"premiere chaine"'
            r'"deuxieme chaine\n"'
            r'"troisieme chainee \"."',
            sName="root")
        self.assertTrue(
            parser.begin_tag('s1') and
            parser.read_cstring() and
            parser.end_tag('s1'),
            'failed in read_cstring for s1')
        s1 = parser.get_tag('s1')
        parser.skip_ignore()
        self.assertEqual(s1, '"premiere chaine"', "failed in capture s1")
        self.assertTrue(
            parser.begin_tag('s2') and
            parser.read_cstring() and
            parser.end_tag('s2'),
            'failed in read_cstring for s2')
        s2 = parser.get_tag('s2')
        parser.skip_ignore()
        self.assertEqual(s2, '"deuxieme chaine\\n"', "failed in capture s2")
        self.assertTrue(
            parser.begin_tag('s3') and
            parser.read_cstring() and
            parser.end_tag('s3'),
            'failed in read_cstring for s3')
        s3 = parser.get_tag('s3')
        self.assertEqual(s3, r'"troisieme chainee \"."',
                         "failed in capture s3")

    def test_06_CallAndSeq(self):
        """
            Basic test for call/clauses
        """
        parser = parsing.Parser()
        parser.parsed_stream("abc def ghg")
        parseTree = parsing.Seq(
            parsing.Call(parsing.Parser.begin_tag, 'i1'),
            parsing.Parser.read_identifier,
            parsing.Call(parsing.Parser.end_tag, 'i1'),
            parsing.Call(parsing.Parser.begin_tag, 'i2'),
            parsing.Parser.read_identifier,
            parsing.Call(parsing.Parser.end_tag, 'i2'),
            parsing.Call(parsing.Parser.begin_tag, 'i3'),
            parsing.Parser.read_identifier,
            parsing.Call(parsing.Parser.end_tag, 'i3'))
        parseTree(parser)
        # Warning! skip_ignore is called between each parsing.Seq
        self.assertEqual(parser.get_tag("i1"), "abc ", "failed in captured i1")
        self.assertEqual(parser.get_tag("i2"), "def ", "failed in captured i2")
        self.assertEqual(parser.get_tag("i3"), "ghg", "failed in captured i3")

    def test_07_RepXN(self):
        """
            Basic test for repeater
        """
        parser = parsing.Parser()
        parser.parsed_stream("12343 91219****1323 23")
        parseTree = parsing.Seq(
            parsing.Call(parsing.Parser.begin_tag, 'i1'),
            parsing.Parser.read_integer,
            parsing.Call(parsing.Parser.end_tag, 'i1'),
            parsing.Rep0N(parsing.Call(parsing.Parser.read_char, '*')),
            parsing.Call(parsing.Parser.begin_tag, 'i2'),
            parsing.Rep1N(parsing.Call(parsing.Parser.read_range, '0', '9')),
            parsing.Call(parsing.Parser.end_tag, 'i2'),
            parsing.Rep0N(parsing.Call(parsing.Parser.read_char, '*')),
            parsing.Call(parsing.Parser.begin_tag, 'i3'),
            parsing.Parser.read_integer,
            parsing.Call(parsing.Parser.end_tag, 'i3'),
            parsing.Call(parsing.Parser.read_eof))
        parseTree(parser)
        # Warning! skip_ignore is called between each parsing.Seq
        self.assertEqual(parser.get_tag("i1"), "12343 ",
                         "failed in captured i1")
        self.assertEqual(parser.get_tag("i2"), "91219",
                         "failed in captured i2")
        self.assertEqual(parser.get_tag("i3"), "1323 ",
                         "failed in captured i3")

    def test_08_RepAlt(self):
        """
            Basic test for alternatives
        """
        parser = parsing.Parser()
        parser.parsed_stream("_ad121dwdw ()[]")
        parseTree = parsing.Seq(
            parsing.Call(parsing.Parser.begin_tag, 'w1'),
            parsing.Scope(
                begin=parsing.Call(parsing.Parser.push_ignore,
                                   parsing.Parser.ignore_null),
                end=parsing.Call(parsing.Parser.pop_ignore),
                pt=parsing.Seq(
                    parsing.Alt(
                        parsing.Call(parsing.Parser.read_char, '_'),
                        parsing.Call(parsing.Parser.read_range, 'a', 'z'),
                        parsing.Call(parsing.Parser.read_range, 'A', 'Z')
                    ),
                    parsing.Rep0N(
                        parsing.Alt(
                            parsing.Call(parsing.Parser.read_char, '_'),
                            parsing.Call(parsing.Parser.read_range, 'a', 'z'),
                            parsing.Call(parsing.Parser.read_range, 'A', 'Z'),
                            parsing.Call(parsing.Parser.read_range,
                                         '0', '9'))))),
            parsing.Call(parsing.Parser.end_tag, 'w1'),
            parsing.Capture(
                'w2',
                parsing.Rep1N(
                    parsing.Alt(
                        parsing.Call(parsing.Parser.read_char, '('),
                        parsing.Call(parsing.Parser.read_char, ')'),
                        parsing.Call(parsing.Parser.read_char, '['),
                        parsing.Call(parsing.Parser.read_char, ']'),
                    )
                )),
            parsing.Call(parsing.Parser.read_eof)
        )
        parseTree.dumpParseTree()
        parseTree(parser)
        # Warning! skip_ignore is called between each parsing.Seq
        self.assertEqual(parser.get_tag("w1"), "_ad121dwdw ",
                         "failed in captured w1")
        self.assertEqual(parser.get_tag("w2"), "()[]",
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
        parser.parsed_stream("asbga    12121      njnj 89898")
        parser.rulenodes[-1]['test'] = self
        parser.set_hooks({'checkWord': check_word, 'checkInt': check_int})
        parser.set_rules({
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
                parsing.Call(parsing.Parser.push_ignore,
                             parsing.Parser.ignore_null),
                parsing.Call(parsing.Parser.pop_ignore),
                parsing.Rep1N(
                    parsing.Alt(
                        parsing.Call(parsing.Parser.read_range, 'a', 'z'),
                        parsing.Call(parsing.Parser.read_range, 'A', 'Z')))),
            'int': parsing.Seq(
                parsing.Scope(
                    parsing.Call(parsing.Parser.push_ignore,
                                 parsing.Parser.ignore_null),
                    parsing.Call(parsing.Parser.pop_ignore),
                    parsing.Capture(
                        'toto',
                        parsing.Rep1N(
                            parsing.Call(parsing.Parser.read_range,
                                         '0', '9')))),
                parsing.Hook(
                    'checkInt',
                    [("test", parsing.Node), ("toto", parsing.Node)]))})
        res = parser.eval_rule('main')
        self.assertTrue(res, "failed to parse")
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
        parser.push_rule_nodes()
        parser.rulenodes[-1].update({'local1': 666, 'local2': 777})
        parser.rulenodes[-1]['toto'] = [1, 2, 3, 4]
        self.assertEqual(parser.rulenodes[-1]['coucou'], 42,
                         "failed outer scope not visible in local")
        parser.pop_rule_nodes()

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
        parsing.Parser.set_one(parsing.Parser._rules, "A.B.C.test", parsing.Call(parsing.Parser.dummy))
        bRes = parser.eval_rule('test')
        self.assertEqual(bRes.text, "cool",
                         "failed rule node in global namespace")
        bRes = parser.eval_rule('C.test')
        self.assertEqual(bRes.text, "cool",
                         "failed rule node in global namespace")
        bRes = parser.eval_rule('B.C.test')
        self.assertEqual(bRes.text, "cool",
                         "failed rule node in global namespace")
        bRes = parser.eval_rule('A.B.C.test')
        self.assertEqual(bRes.text, "cool",
                         "failed rule node in global namespace")


    def test_12_Metabasicparser(self):
        """
        Test the metaclass of BasicParser
        """
        class   A(metaclass=parsing.MetaBasicParser):
            pass
        self.assertTrue('_rules' in dir(A), "failed metaclass don't add _rules")
        self.assertIsInstance(A._rules, collections.ChainMap, "failed _rules is not a ChainMap")
        self.assertTrue('_hooks' in dir(A), "failed metaclass don't add _hooks")
        self.assertIsInstance(A._hooks, collections.ChainMap, "failed _hooks is not a ChainMap")
        self.assertTrue('_directives' in dir(A), "failed metaclass don't add _directives")
        self.assertIsInstance(A._directives, collections.ChainMap, "failed _directives is not a ChainMap")

    def test_13_defaultRules(self):
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
