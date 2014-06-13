import unittest
import os
import importlib
from pyrser import meta
from pyrser import grammar
from pyrser.parsing import functors
from pyrser.passes import to_yml
from pyrser.codegen.c import cython
from pyrser import error


class GenDsl_Test(unittest.TestCase):
    
    def test_000_init(self):
        os.makedirs('build_cython', exist_ok=True);
        # add  the path for modules
        import sys
        sys.path.append('./build_cython')

    def test_00_seqchar(self):
        """Test sequence and char
        """
        class SeqChar(grammar.Grammar):
            entry = "test"
            grammar = """test = [ 'a' 'c' 'b' 'e' ]
            """
        p = SeqChar()
        cython.generate(p, indir='build_cython', keep_tmp=True)
        primit = importlib.import_module('build_cython.seqchar')
        p = primit.SeqChar("acbe")
        res = p.test()
        self.assertTrue(res, "Bad parsing")
        p = primit.SeqChar("acb")
        res = p.test()
        self.assertFalse(res, "Bad parsing")
        p = primit.SeqChar("coucou")
        res = p.test()
        self.assertFalse(res, "Bad parsing")

    def test_01_altchar(self):
        """Test alternative and char
        """
        class AltChar(grammar.Grammar):
            entry = "test"
            grammar = """test = [ 'a' ['c' | 'b' ['e' | 'z'] ] 'd']
            """
        p = AltChar()
        cython.generate(p, indir='build_cython', keep_tmp=True)
        primit = importlib.import_module('build_cython.altchar')
        p = primit.AltChar("coucou")
        res = p.test()
        self.assertFalse(res, "Bad parsing")
        p = primit.AltChar("acd")
        res = p.test()
        self.assertTrue(res, "Bad parsing")
        p = primit.AltChar("abed")
        res = p.test()
        self.assertTrue(res, "Bad parsing")
        p = primit.AltChar("abzd")
        res = p.test()
        self.assertTrue(res, "Bad parsing")
        p = primit.AltChar("abd")
        res = p.test()
        self.assertFalse(res, "Bad parsing")

    def test_02_text(self):
        """Test gen text
        """
        class Text(grammar.Grammar):
            entry = "test"
            grammar = """test = ["hello"|"world"]
            """
        p = Text()
        cython.generate(p, indir='build_cython')
        primit = importlib.import_module('build_cython.text')
        p = primit.Text("hello")
        res = p.test()
        self.assertTrue(res, "Bad parsing")
        p = primit.Text("world")
        res = p.test()
        self.assertTrue(res, "Bad parsing")
        p = primit.Text("abed")
        res = p.test()
        self.assertFalse(res, "Bad parsing")
        p = primit.Text("helworld")
        res = p.test()
        self.assertFalse(res, "Bad parsing")
        p = primit.Text("helloworld")
        res = p.test()
        self.assertTrue(res, "Bad parsing")

    def test_03_number(self):
        """Test gen number
        """
        class Number(grammar.Grammar):
            entry = "test"
            grammar = """test = [ ['0'..'9']* | "coucou" ]
            """
        p = Number()
        cython.generate(p, indir='build_cython', keep_tmp=True)
        primit = importlib.import_module('build_cython.number')
        p = primit.Number("12")
        res = p.test()
        self.assertTrue(res, "Bad parsing")
        p = primit.Number("123hy")
        res = p.test()
        self.assertTrue(res, "Bad parsing")
        p = primit.Number("abed")
        res = p.test()
        self.assertFalse(res, "Bad parsing")
        p = primit.Number("coucou")
        res = p.test()
        self.assertTrue(res, "Bad parsing")

    def test_03_number2(self):
        """Test gen number2
        """
        class Number2(grammar.Grammar):
            entry = "test"
            grammar = """test = [ ['0'..'9' | '_']+ ]
            """
        p = Number2()
        cython.generate(p, indir='build_cython', keep_tmp=True)
        primit = importlib.import_module('build_cython.number2')
        p = primit.Number2("12")
        res = p.test()
        self.assertTrue(res, "Bad parsing")
        p = primit.Number2("_")
        res = p.test()
        self.assertTrue(res, "Bad parsing")
        p = primit.Number2("abed")
        res = p.test()
        self.assertFalse(res, "Bad parsing")
        p = primit.Number2("")
        res = p.test()
        self.assertFalse(res, "Bad parsing")
        p = primit.Number2("12__23_123414232_123")
        res = p.test()
        self.assertTrue(res, "Bad parsing")

    def test_04_optional(self):
        """Test gen optional
        """
        class Optional(grammar.Grammar):
            entry = "test"
            grammar = """test = [ ['!']? 'A' | ['?']? 'B' ]
            """
        p = Optional()
        cython.generate(p, indir='build_cython', keep_tmp=True)
        primit = importlib.import_module('build_cython.optional')
        p = primit.Optional("A")
        res = p.test()
        self.assertTrue(res, "Bad parsing")
        p = primit.Optional("B")
        res = p.test()
        self.assertTrue(res, "Bad parsing")
        p = primit.Optional("!A")
        res = p.test()
        self.assertTrue(res, "Bad parsing")
        p = primit.Optional("?B")
        res = p.test()
        self.assertTrue(res, "Bad parsing")
        p = primit.Optional("!?B")
        res = p.test()
        self.assertFalse(res, "Bad parsing")

    def test_05_neg(self):
        """Test gen neg
        """
        class Neg(grammar.Grammar):
            entry = "test"
            grammar = """test = [ '=' !'=' ]
            """
        p = Neg()
        cython.generate(p, indir='build_cython', keep_tmp=True)
        primit = importlib.import_module('build_cython.neg')
        p = primit.Neg("=")
        res = p.test()
        self.assertTrue(res, "Bad parsing")
        p = primit.Neg("==")
        res = p.test()
        self.assertFalse(res, "Bad parsing")
        p = primit.Neg("=a")
        res = p.test()
        self.assertTrue(res, "Bad parsing")

    def test_06_complement(self):
        """Test gen complement
        """
        try:
            class Complement(grammar.Grammar):
                entry = "test"
                #grammar = """test = [ '"' [~"\\\\" | "\\\\" ~' ']* '"' ]
                #"""
                grammar = """
                    test = [ [~'A']+ 'A' ]
                """
        except error.Diagnostic as d:
            print(d.get_content())
            raise d
        p = Complement()
        cython.generate(p, indir='build_cython', keep_tmp=True)
        primit = importlib.import_module('build_cython.complement')
        p = primit.Complement("CDBA")
        res = p.test()
        self.assertTrue(res, "Bad parsing")
        p = primit.Complement("A")
        res = p.test()
        self.assertFalse(res, "Bad parsing")
        p = primit.Complement("C +\`3BA")
        res = p.test()
        self.assertTrue(res, "Bad parsing")
        p = primit.Complement("C[]")
        res = p.test()
        self.assertFalse(res, "Bad parsing")

    def test_07_string(self):
        """Test gen string
        """
        try:
            class String(grammar.Grammar):
                entry = "test"
                grammar = """
                    test = [ '"' [ ~["\\\\"|'"'] | "\\\\" ~' ']* '"' ]
                """
        except error.Diagnostic as d:
            print(d.get_content())
            raise d
        p = String()
        cython.generate(p, indir='build_cython', keep_tmp=True)
        primit = importlib.import_module('build_cython.string')
        # TODO: Why I can't pass the following test?
        #p = primit.String('""')
        #res = p.test()
        #self.assertTrue(res, "Bad parsing")
        p = primit.String('" "')
        res = p.test()
        self.assertTrue(res, "Bad parsing")
        p = primit.String('"toto"')
        res = p.test()
        self.assertTrue(res, "Bad parsing")
        p = primit.String('"lolo\\"kiki"')
        res = p.test()
        self.assertTrue(res, "Bad parsing")
        p = primit.String('"lolo\\"')
        res = p.test()
        self.assertFalse(res, "Bad parsing")
        p = primit.String('"lolo\\ kiki"')
        res = p.test()
        self.assertFalse(res, "Bad parsing")

    def test_08_lookahead(self):
        """Test gen lookahead
        """
        try:
            class LookAhead(grammar.Grammar):
                entry = "test"
                grammar = """
                    test = [ !!["toto"| '0'..'9'] ["toto"| '0'..'9' ['0'..'9']+ ] | !'0'..'9' ~' ' ]
                """
        except error.Diagnostic as d:
            print(d.get_content())
            raise d
        p = LookAhead()
        cython.generate(p, indir='build_cython', keep_tmp=True)
        primit = importlib.import_module('build_cython.lookahead')
        p = primit.LookAhead('123')
        res = p.test()
        self.assertTrue(res, "Bad parsing")
        p = primit.LookAhead('toto')
        res = p.test()
        self.assertTrue(res, "Bad parsing")
        p = primit.LookAhead('t')
        res = p.test()
        self.assertTrue(res, "Bad parsing")
        p = primit.LookAhead('1t')
        res = p.test()
        self.assertFalse(res, "Bad parsing")

    def test_09_until(self):
        """Test gen until
        """
        try:
            class Until(grammar.Grammar):
                entry = "test"
                grammar = """
                    test = [ 'a'..'z'+ ->'A'..'Z' 'A'..'Z'+ ]
                """
        except error.Diagnostic as d:
            print(d.get_content())
            raise d
        p = Until()
        cython.generate(p, indir='build_cython', keep_tmp=True)
        primit = importlib.import_module('build_cython.until')
        p = primit.Until('blabla +- TOTO')
        res = p.test()
        self.assertTrue(res, "Bad parsing")

    def test_zzz_fini(self):
        import shutil
        shutil.rmtree('build_cython')
