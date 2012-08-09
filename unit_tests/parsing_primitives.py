from asciiParse import AsciiParseWrapper
import unittest

class AsciiParseUnitTest(unittest.TestCase):
      """docstring for AsciiParseUnitTest"""
      def i(self):
          """ helper to get current index """
          return self.w.getIndex()

      def n(self, string):
          """docstring for n"""
	  self.w = AsciiParseWrapper(string)
          
      def test_init(self):
          """docstring for runTest"""
	  print\
	  '----------------------------------------------------------------------\n'
	  self.n('')
	  self.assertEqual(self.i(), 0, 'failed in .Ctor : [%d]' %
	      self.i())
	  print 'w = AsciiParseWrapper("a string")'
          self.s = 'abc'

      def test_readChar_and_peekChar(self):
          """docstring for test_readChar_and_peekChar"""
	  print '-------------------------\n'
	  self.n('abc')
	  self.assertEqual(
	      (self.w.readChar('a') and self.i() == 1),
	      True, 'failed in readChar')
	  print 'w.readChar("a")'

      def test_readWs(self):
          """docstring for test_readWs"""
	  print '-------------------------\n'
	  self.n('    notspace')
	  self.assertEqual(
	      (self.w.readWs() and self.i() == 4),
	      True, 'failed in readWs : [%d]' % self.i())
	  print 'w.readWs("      notspace")'

      def test_readUntil(self):
	  """ check readUntil function"""
	  print '-------------------------\n'
	  self.n('a[..]z')
	  self.w.readUntil('z', '\\')
	  self.assertEqual(
	    self.w.readEOF(),
	    True, 'failed in readUntil : [%d]' % self.i())
	  print 'w.readUntil("z") where w.stream is "a[..]z"'
	  
	  self.n("'abc \\' def' gh")
	  self.w.readChar("'")
	  self.w.readUntil("'", '\\')
	  self.w.readWs()
	  self.assertEqual(
	    self.w.readText('gh'),
	    True, 'failed in readUntil inhibitor : [%d]' % self.i())
	  print 'w.readUntil("z") where w.stream is "\'abc \\\' def\' gh"'

      def test_readUntilEOF(self):
          """docstring for test_readUntilEOF"""
	  print '-------------------------\n'
	  self.n('[abc]')
	  self.w.readUntilEOF()
	  self.assertEqual(
	      self.w.readEOF(),
	      True, 'failed in readUntilEOF : [%d]' % self.i())
	  print 'w.readUntilEOF() where w.stream is "[abc]"'
         
      def test_ColonContext(self):
	  """
	  test Context features :
	    - Colon number
	    - Line number
	  """
	  self.n('abc')
	  self.w.readUntil('b')
	  self.assertEqual(self.i(), 2, 'failed in colons context maintain')

      
      def test_LineContext(self):
          """docstring for test_LineContext"""
	  self.n('abc\ndef')
	  self.w.readUntilEOF()
	  self.assertEqual(self.w.getLineNbr(), 2, 'failed in line context\
	      maintain')

      def test_readText(self):
          """docstring for test_readText"""
	  print '-------------------------\n'
          self.n('#text usefull')
	  self.w.readText('#text')
	  self.assertEqual(self.i(), 5, 'failed in readText : [%d]' % self.i())
	  print 'w.readText("#text")'
          
	  self.n('#text usefull')
	  self.w.saveContext()
	  self.w.readText('#text')
	  self.w.restoreContext()
	  self.assertEqual(self.i(), 0, 'failed in readText : [%d]' % self.i())
	  print 'w.readText("#text") with context restoration'

      def test_readInteger(self):
          """docstring for test_readInteger"""
          print '-------------------------\n'
          self.n('12345 usefull')
	  self.w.readInteger()
	  self.assertEqual(self.i(), 5, 'failed in readInteger : [%d]' % self.i())
	  print 'w.readText() where w.stream is "12345 usefull"'

      def test_readIdentifier(self):
          """docstring for test_readIdentifier"""
          print '-------------------------\n'
          self.n('_i123$1')
	  self.w.readIdentifier()
	  self.assertEqual(self.i(), 5, 'failed in readIdentifier : [%d]' % self.i())
	  print 'w.readIdentifier() where w.stream is "_i123$1"'
          
	  self.n('K')
	  self.w.readIdentifier()
	  self.assertEqual(self.i(), 1, 'failed in readIdentifier : [%d]' % self.i())
	  print 'w.readIdentifier() where w.stream is "K"'

      def test_readRange(self):
          """docstring for test_readRange"""
          print '-------------------------\n'
          self.n('vzwyxa')
	  self.w.readRange('v', 'z')
	  self.assertEqual(self.i(), 1, 'failed in readRange : [%d]' % self.i())
	  print 'w.readRange("v", "z") where w.stream is "vzwyxa"'

      def test_readCString(self):
          """docstring for test_readCString"""
          print '-------------------------\n'
          self.n('"abc" def')
	  self.w.readCString()
	  self.assertEqual(self.i(), 5, 'failed in readCString : [%d]' % self.i())
	  print 'w.readCString where string is \'\"abc\" def\''

      def test_readCChar(self):
          print '-------------------------\n'
          self.n("'c' def")
	  self.w.readCChar()
	  self.assertEqual(self.i(), 3, 'failed in readCChar : [%d]' % self.i())
	  print 'w.readCChar where string is \"\'a\' def\"'

          self.n("'c' def")
	  self.w.saveContext()
	  before = self.i()
	  self.w.readCChar()
	  after = self.i()
	  self.w.restoreContext()
	  self.assertEqual(self.i(), 0,\
	      'failed in readCChar restore : before :[%d]\
	      : after [%d] : final [%d]' %\
	      (before, after, self.i()))
	  print 'w.readCChar restoration where string is \"\'a\' def\"'

      def test_failreadCString(self):
          """ Test Fail Cases of readCString """
 
          self.n('"abc def')
	  self.w.readCString()
	  self.assertEqual(self.i(), 0, 'failed in readCString : [%d]' % self.i())

      def test_failreadCChar(self):
          """docstring for test_failreadCChar"""
          self.n("'a def")
	  self.w.readCChar()
	  self.assertEqual(self.i(), 0, 'failed in readCString : [%d]' % self.i())
  
      def test_zchangeStream(self):
          """docstring for test_changeStream"""
          print '-------------------------\n'
          self.n('abc def')
	  self.w.readUntil(' ')
	  self.w.parsedStream('xyz', 'woot')
	  self.assertEqual(self.w.getName(), 'woot',\
	      'failed while changing current stream : [%d]' % self.i())
	  self.w.readUntilEOF()
	  self.assertEqual(self.w.readEOF(), True,\
	      'failed while changing current stream : [%d]' % self.i())
	  self.w.popStream()
	  self.assertEqual(self.w.readChar('d'), True,\
	      'failed while changing current stream : [%d]' % self.i())
	  print 'Stream change and context restauration.'

      def test_saveAndRestoreContext(self):
          """docstring for test_saveContext"""
          print '-------------------------\n'
          self.n('abc def')
	  self.w.saveContext()
	  self.w.readUntil(' ')
	  self.w.restoreContext()
	  self.assertEqual(self.i(), 0,\
	      'failed while saving/restoring context : [%d]' % self.i())
	  print 'Context saving and restoration'

      def test_capture(self):
          """docstring for test_getStream"""
          print '-------------------------\n'
          self.n('abc def')
	  self.w.setTag('tag')
	  self.w.readIdentifier()
	  res = self.w.getTag('tag')
	  self.assertEqual(res, 'abc',\
	      'failed while extract by tag : [%d]' % self.i())
	  print 'Capture/extract string'


          
if __name__ == '__main__':
	unittest.main()
	print 'All tests ran successfully'
