import unittest
from pyrser.grammar import Grammar


class CaptureGeneration(Grammar):
    grammar = """
      parentTest ::= #num :test captureTest
      ;

      captureTest ::= #identifier :test #test
      ;
      """
#      def __init__(self):
#          super(CaptureGeneration, self).__init__(CaptureGeneration,
#                                                  CaptureGeneration.__doc__)

    def testHook(self, oTreeContext):
        return True


class Capture_Test(unittest.TestCase):
    @classmethod
    def setUpClass(cCaptureClass):
        cCaptureClass.oRoot = {}
        cCaptureClass.oGrammar = CaptureGeneration()

    def test_capture(self):
        self.assertEqual(
            Capture_Test.oGrammar.parse('123 id', self.oRoot, 'parentTest'),
            True,
            'failed in capture')
