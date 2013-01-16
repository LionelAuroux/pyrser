from pyrser.parsing.python.asciiParse import AsciiParseWrapper
# from pyrser.parsing.cpp.asciiParse import AsciiParseWrapper
import unittest


class AsciiParseUnitTest(unittest.TestCase):
    def i(self):
        """ helper to get current index """
        return self.w.index()
#          return self.w.getIndex()

    def n(self, string):
        self.w = AsciiParseWrapper(string)

    def test_init(self):
        self.n('')
        self.assertEqual(self.i(), 0, 'failed in .Ctor : [%d]' %
                         self.i())
        self.s = 'abc'

    def test_readChar_and_peekChar(self):
        self.n('abc')
        self.assertEqual(
            (self.w.readChar('a') and self.i() == 1),
            True, 'failed in readChar/peekChar')

    def test_readWs(self):
        self.n('    notspace')
        self.w.readWs()
        self.assertEqual(
            (self.i() == 4),
            True, 'failed in readWs : [%d]' % self.i())

    def test_monoline_comment(self):
        pass

    def test_multiline_comment(self):
        pass

    def test_readUntil(self):
        self.n('a[..]z')
        self.w.readUntil('z', '\\')
        self.assertEqual(
            self.w.readEOF(),
            True, 'failed in readUntil : [%d]' % self.i())
        self.assertEqual(self.i(),
                         6, 'failed in readUntil : [%d]' % self.i())

        self.n("'abc \\' def' gh")
        self.w.readChar("'")
        self.w.readUntil("'", '\\')
        self.w.readWs()
        self.assertEqual(
            self.w.readText('gh'),
            True, 'failed in readUntil inhibitor : [%d]' % self.i())

    def test_readUntilEOF(self):
        self.n('[abc]')
        self.w.readUntilEOF()
        self.assertEqual(
            self.w.readEOF(),
            True, 'failed in readUntilEOF : [%d]' % self.i())

    def test_ColonContext(self):
        # FIXME : complete on line test
        self.n('abc')
        self.assertEqual(self.w.readUntil('b'), True,
                         'failed in colons context maintain (False) : [%s]' % self.i())
        self.assertEqual(self.i(), 2,
                         'failed in colons context maintain (Index is wrong) : [%s]' % self.i())

    def test_LineContext(self):
        self.n('abc\ndef')
        self.w.readUntilEOF()
        self.assertEqual(self.w.getLineNbr(), 2, 'failed in line context\
	      maintain')

    def test_readText(self):
        self.n('#text usefull')
        self.w.readText('#text')
        self.assertEqual(self.i(), 5, 'failed in readText : [%d]' % self.i())

        self.n('#text usefull')
        self.w.saveContext()
        self.w.readText('#text')
        self.w.restoreContext()
        self.assertEqual(self.i(), 0, 'failed in readText : [%d]' % self.i())

    def test_readInteger(self):
        self.n('12345 usefull')
        self.w.readInteger()
        self.assertEqual(
            self.i(), 5, 'failed in readInteger : [%d]' % self.i())

    def test_readIdentifier(self):
        self.n('_i123$1')
        self.w.readIdentifier()
        self.assertEqual(
            self.i(), 5, 'failed in readIdentifier : [%d]' % self.i())

        self.n('K')
        self.w.readIdentifier()
        self.assertEqual(
            self.i(), 1, 'failed in readIdentifier : [%d]' % self.i())

    def test_readRange(self):
        self.n('vzwyxa')
        self.w.readRange('v', 'z')
        self.assertEqual(self.i(), 1, 'failed in readRange : [%d]' % self.i())

    def test_readCString(self):
        self.n('"abc" def')
        self.w.readCString()
        self.assertEqual(
            self.i(), 5, 'failed in readCString : [%d]' % self.i())

    def test_readCChar(self):
        self.n("'c' def")
        self.w.readCChar()
        self.assertEqual(self.i(), 3, 'failed in readCChar : [%d]' % self.i())

        self.n("'c' def")
        self.w.saveContext()
        before = self.i()
        self.w.readCChar()
        after = self.i()
        self.w.restoreContext()
        self.assertEqual(self.i(), 0,
                         'failed in readCChar restore : before :[%d]\
	      : after [%d] : final [%d]' %
                        (before, after, self.i()))

    def test_failreadCString(self):
        self.n('"abc def')
        self.w.readCString()
        self.assertEqual(
            self.i(), 0, 'failed in readCString : [%d]' % self.i())

    def test_failreadCChar(self):
        self.n("'a def")
        self.w.readCChar()
        self.assertEqual(self.i(), 0, 'failed in readCChar : [%d]' % self.i())

    def test_changeStream(self):
        self.n('abc def')
        self.w.readUntil(' ')
#	  self.w.readIdentifier()
        self.w.parsedStream('xyz', 'woot')
        self.assertEqual(self.w.getName(), 'woot',
                         'failed while changing current stream : [%d]' % self.i())
        self.w.readUntilEOF()
        self.assertEqual(self.w.readEOF(), True,
                         'failed while changing current stream : [%d]' % self.i())
        self.w.popStream()
        self.assertEqual(self.w.readChar('d'), True,
                         'failed while changing current stream : [%d]' % self.i())

    def test_saveAndRestoreContext(self):
        self.n('abc def')
        self.w.saveContext()
        self.w.readUntil(' ')
        self.w.restoreContext()
        self.assertEqual(self.i(), 0,
                         'failed while saving/restoring context : [%d]' % self.i())

    def test_capture(self):
        self.n('abc def')
        self.w.setTag('tag')
        self.w.readIdentifier()
        res = self.w.getTag('tag')
        self.assertEqual(res, 'abc',
                         'failed while extract by tag : [%d]' % self.i())

if __name__ == '__main__':
    unittest.main()
