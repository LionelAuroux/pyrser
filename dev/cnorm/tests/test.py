from pprint import pprint
from pyrser.node import clean_tree
from pyrser.grammar import runtime_error_handle
from cnorm_to_c.cnorm_to_c import c_ast_to_c


def test(lTest, oGrammarParser, sTemplateName, sFirst):
    bExceptionInHook = False
    sTr = '-' * 80
    for iTest in lTest:
        print "%s\n%s" % (sTr, iTest)
        oRoot = {}
        bRes = oGrammarParser.parse(iTest, oRoot, sFirst)
        pprint(oRoot)
        if not bRes:
            raise Exception("Parse test failed : %s" % iTest)
        sRes = c_ast_to_c(oRoot, sTemplateName)
        if sRes != iTest:
            raise Exception(
                "CNorm2c test failed :\nTest : %s\n%s\n%s\n!=\nResultalt : %s\n%s"
                % (sTr, iTest, sTr, sTr, sRes))
    return bExceptionInHook
