import collections
import unittest
from unittest import mock

from pyrser import parsing
from pyrser import meta
from pyrser import grammar
from pyrser.passes import dumpParseTree


class InternalParse_Test(unittest.TestCase):
    def test_00_Directive(self):
        """Test Directive/DirectiveWrapper
        """
        class DummyDirective(parsing.DirectiveWrapper):
            def begin(self, test, a: int, b: int):
                test.assertEqual(a, 1)
                test.assertEqual(b, 2)
                return True

            def end(self, test, a: int, b: int):
                test.assertEqual(a, 1)
                test.assertEqual(b, 2)
                return True

        def dummyParser(p):
            return True
        direct = parsing.Directive(DummyDirective(), [(1, int), (2, int)],
                                   dummyParser)
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
            Basic test for repeater operator
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
        parser.rulenodes['test'] = self
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
        parser.rulenodes.update({'coucou': 42, 'grigri': 666, 'toto': [12, 33]})
        self.assertEqual(parser.rulenodes['toto'], [12, 33],
                         "failed comparing list")
        parser.push_rule_nodes()
        parser.rulenodes.update({'local1': 666, 'local2': 777})
        parser.rulenodes['toto'] = [1, 2, 3, 4]
        self.assertEqual(parser.rulenodes['coucou'], 42,
                         "failed outer scope not visible in local")
        parser.push_rule_nodes()
        self.assertEqual(parser.rulenodes['grigri'], 666,
                         "failed outer scope not visible in local")
        self.assertTrue('grigri' in parser.rulenodes, "failed outer scope not visible in local")
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
            self.rulenodes["_"].set(res)
            return res
        meta.set_one(parsing.Parser._rules, "A.B.C.test",
                     parsing.Call(parsing.Parser.dummy))
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
        class FakeBasic(metaclass=parsing.MetaBasicParser):
            _rules = collections.ChainMap()
            _hooks = collections.ChainMap()
            pass

        class A(FakeBasic):
            pass

        class B(FakeBasic):
            _rules = {'key': 'value'}
            _hooks = {'key': 'value'}

        self.assertTrue('_rules' in dir(A))
        self.assertIsInstance(A._rules, collections.ChainMap)
        self.assertTrue('_hooks' in dir(A))
        self.assertIsInstance(A._hooks, collections.ChainMap)
        self.assertEqual(id(A), id(parsing.parserBase._MetaBasicParser['A']),
                         "failed to found metaclass A in global registry")
        self.assertEqual(id(B._rules.maps[1]), id(FakeBasic._rules.maps[0]),
                         "failed to chain FakeBasic._rules and B._rules")
        self.assertEqual(id(B._hooks.maps[1]), id(FakeBasic._hooks.maps[0]),
                         "failed to chain FakeBasic._hooks and B._hooks")
        FakeBasic._rules['newrule'] = 'oldvalue'
        FakeBasic._hooks['newhook'] = 'oldvalue'
        self.assertIn('newrule', B._rules,
                      "failed global modification in FakeBasic._rules"
                      " not impacted in B._rules")
        self.assertIn('newhook', B._hooks,
                      "failed global modification in FakeBasic._hooks"
                      " not impacted in B._hooks")
        B._rules['newrule'] = 'newvalue'
        B._hooks['newhook'] = 'newvalue'
        self.assertEqual(B._rules['newrule'], 'newvalue',
                         "failed in local rules modification")
        self.assertEqual(B._hooks['newhook'], 'newvalue',
                         "failed in local hooks modification")
        self.assertEqual(FakeBasic._rules['newrule'], 'oldvalue',
                         "failed local rules modification must be local")
        self.assertEqual(FakeBasic._hooks['newhook'], 'oldvalue',
                         "failed local hooks modification must be local")

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

    def test_14_MetaGrammar(self):
        """
        Test the metaclass of Grammar
        """
        class FakeGrammar(metaclass=grammar.MetaGrammar):
            pass

        class SubGrammar(parsing.Parser, FakeGrammar):
            pass

        # TODO:
        #print("Test Grammar")

    def test_15_error_index(self):
        """
        Test error index
        """
        parser = parsing.Parser()
        parser.parsed_stream("bla\n12abcd\nblu")
        self.assertTrue(parser.read_text("bla\n") and parser.read_integer(),
                        "failed to parse begin of stream")
        self.assertTrue(not parser.read_text("abcde"),
                        "failed to not parse abcde")
        self.assertEqual(parser._stream[parser._stream._cursor
                         .max_readed_position.index],
                         'a',
                         "failed when checking the correction position of last"
                         " readed character")
        self.assertEqual(parser._stream.last_readed_line, "12abcd",
                         "failed to get the correct last readed line")

    def test_16_Negation(self):
        """
        Basic test for negation !R
        """
        parser = parsing.Parser()
        parser.parsed_stream("==")
        parseTree = \
            parsing.Seq(parsing.Call(parsing.Parser.read_char, '='),
                        parsing.Neg(parsing.Call(
                            parsing.Parser.read_char,
                            '=')))
        parseTree.dumpParseTree()
        res = parseTree(parser)
        self.assertEqual(res, False, "failed to get the correct final value")
        self.assertEqual(vars(parser._stream._cursor)['_Cursor__index'], 0,
                         "failed to get the correct index after a negation")

    def test_17_Lookahead(self):
        """
        Basic test for lookahead !!R
        """
        parser = parsing.Parser()
        parser.parsed_stream("==")
        parseTree = \
            parsing.Seq(parsing.Call(parsing.Parser.read_char, '='),
                        parsing.LookAhead(parsing.Call(
                            parsing.Parser.read_char,
                            '=')),
                        )
        parseTree.dumpParseTree()
        res = parseTree(parser)
        self.assertEqual(res, True, "failed to get the correct final value")
        self.assertEqual(vars(parser._stream._cursor)['_Cursor__index'], 1,
                         "failed to get the correct index after a lookahead")

    def test_18_Complement(self):
        """
        Basic test for complement ~R
        """
        parser = parsing.Parser()
        parser.parsed_stream("==")
        parseTree = parsing.Seq(
            parsing.Call(parsing.Parser.read_char, '='),
            parsing.Complement(parsing.Call(parsing.Parser.read_char, '=')))
        parseTree.dumpParseTree()
        res = parseTree(parser)
        self.assertEqual(res, False, "failed to get the correct final value")
        self.assertEqual(vars(parser._stream._cursor)['_Cursor__index'], 0,
                         "failed to get the correct index after a lookahead")
        parser.parsed_stream("=+")
        res = parseTree(parser)
        self.assertEqual(res, True, "failed to get the correct final value")
        self.assertEqual(vars(parser._stream._cursor)['_Cursor__index'], 2,
                         "failed to get the correct index after a lookahead")

    def test_19_Until(self):
        """
        Basic test for complement ->R
        """
        parser = parsing.Parser()
        parser.parsed_stream("==|=|==tutu")
        parseTree = parsing.Seq(
            parsing.Until(parsing.Call(parsing.Parser.read_text, '|==')),
            parsing.Call(parsing.Parser.read_text, 'tutu'),
            )
        parseTree.dumpParseTree()
        res = parseTree(parser)
        self.assertEqual(res, True, "failed to get the correct final value")
