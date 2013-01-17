import unittest
from pyrser.parsing.python.AsciiParseWrapper import AsciiParseWrapper

class InternalParse_Test(unittest.TestCase):
    @classmethod
    def setUpClass(cInternalParseClass):
        cInternalParseClass.oParse = AsciiParseWrapper()
        cInternalParseClass.oParse.popStream()

    def test_readIdentifier(self):
        """
            Basic test for identifier parsing
        """
        oParse = InternalParse_Test.oParse
        oParse.parsedStream("ceci est un test", sName = "root")
        self.assertTrue(
            oParse.setTag('sujet') and oParse.readIdentifier(),
            'failed in readIdentifier for sujet')
        sujet = oParse.getTag('sujet')
        self.assertEqual(sujet, "ceci", "failed in capture sujet")
        self.assertTrue(
            oParse.setTag('verbe') and oParse.readIdentifier(),
            'failed in readIdentifier for verbe')
        verbe = oParse.getTag('verbe')
        self.assertEqual(verbe, "est", "failed in capture verbe")
        self.assertTrue(
            oParse.setTag('other') and oParse.readUntilEOF(),
            'failed in readIdentifier for other')
        reste = oParse.getTag('other')
        self.assertEqual(reste, "un test", "failed in capture other")

    def test_readInteger(self):
        """
            Basic test for integer parsing
        """
        oParse = InternalParse_Test.oParse
        oParse.parsedStream("12 333 44444444444444444444444444", sName = "root")
        self.assertTrue(
            oParse.setTag('n1') and oParse.readInteger(),
            'failed in readInteger for n1')
        n1 = oParse.getTag('n1')
        self.assertEqual(n1, "12", "failed in capture n1")
        self.assertTrue(
            oParse.setTag('n2') and oParse.readInteger(),
            'failed in readInteger for n2')
        n2 = oParse.getTag('n2')
        self.assertEqual(n2, "333", "failed in capture n2")
        self.assertTrue(
            oParse.setTag('n3') and oParse.readInteger(),
            'failed in readInteger for n3')
        n3 = oParse.getTag('n3')
        self.assertEqual(n3, "44444444444444444444444444", "failed in capture n3")

    def test_linecol(self):
        """
            Basic test for line/col calculation
        """
        oParse = InternalParse_Test.oParse
        oParse.parsedStream("X\nXX\nXXX\n")
        line = oParse.getLineNbr()
        col = oParse.getColumnNbr()
        self.assertTrue(line == 1 and col == 1, "failed line/col at beginning")
        oParse.incPos()
        oParse.incPos()
        line = oParse.getLineNbr()
        col = oParse.getColumnNbr()
        self.assertTrue(line == 2 and col == 1, "failed line/col at second")
        oParse.incPos()
        oParse.incPos()
        oParse.incPos()
        line = oParse.getLineNbr()
        col = oParse.getColumnNbr()
        self.assertTrue(line == 3 and col == 1, "failed line/col at third")
        oParse.incPos()
        oParse.incPos()
        col = oParse.getColumnNbr()
        self.assertTrue(line == 3 and col == 3, "failed line/col at col")
        oParse.incPos()
        oParse.incPos()
        line = oParse.getLineNbr()
        col = oParse.getColumnNbr()
        self.assertTrue(line == 4 and col == 1, "failed line/col at forth")

    def test_readCChar(self):
        """
            Basic test for readCChar
        """
        oParse = InternalParse_Test.oParse
        oParse.parsedStream("'c' '\\t'", sName = "root")
        self.assertTrue(
            oParse.setTag('c1') and oParse.readCChar(),
            'failed in readCChar for c1')
        c1 = oParse.getTag('c1')
        self.assertEqual(c1, "'c'", "failed in capture c1")
        self.assertTrue(
            oParse.setTag('c2') and oParse.readCChar(),
            'failed in readCChar for c2')
        c2 = oParse.getTag('c2')
        self.assertEqual(c2, "'\\t'", "failed in capture c2")

    def test_readCString(self):
        """
            Basic test for readCString
        """
        oParse = InternalParse_Test.oParse
        oParse.parsedStream('"premiere chaine" "deuxieme chaine\\n" "troisieme chainee \\"."', sName = "root")
        self.assertTrue(
            oParse.setTag('s1') and oParse.readCString(),
            'failed in readCString for s1')
        s1 = oParse.getTag('s1')
        self.assertEqual(s1, '"premiere chaine"', "failed in capture s1")
        self.assertTrue(
            oParse.setTag('s2') and oParse.readCString(),
            'failed in readCString for s2')
        s2 = oParse.getTag('s2')
        self.assertEqual(s2, '"deuxieme chaine\\n"', "failed in capture s2")
        self.assertTrue(
            oParse.setTag('s3') and oParse.readCString(),
            'failed in readCString for s3')
        s3 = oParse.getTag('s3')
        self.assertEqual(s3, '"troisieme chainee \\"."', "failed in capture s3")

