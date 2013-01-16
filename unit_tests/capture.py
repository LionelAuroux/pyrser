import unittest
from pyrser.grammar import Grammar


class CaptureGeneration(Grammar):
    """
    parentTest ::= #num :test captureTest
    ;

    captureTest ::= #identifier :test #test
    ;
    """
    def __init__(self):
        super(CaptureGeneration, self).__init__(CaptureGeneration,
                                                CaptureGeneration.__doc__)

    def testHook(self, oTreeContext):
        return True


class generatedCode(unittest.TestCase):
    @classmethod
    def setUpClass(cGeneratedCodeClass):
        cGeneratedCodeClass.oRoot = {}
        cGeneratedCodeClass.oGrammar = CaptureGeneration()

    def test_capture(self):
        self.assertEqual(
            generatedCode.oGrammar.parse('123 id', self.oRoot, 'parentTest'),
            True,
            'failed in capture')
