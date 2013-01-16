from pyrser.grammar import Grammar
from pyrser.hooks import GenericHook
from expression import CExpression


class CStatement(GenericHook, Grammar):
    def __init__(self):
        GenericHook.__init__(self)
        Grammar.__init__(self, CStatement,
                         open("./grammar/statement.pw").read(),
                         globals())

    def typeHook(self, oNode, sSubExpr, sType="__statement__"):
        """
        Type should attribute an automatic name: per grammar function.
        """
        oNode["type"] = sType
        oNode["sub_type"] = sSubExpr
        return oNode

if __name__ != '__main__':
    CStatement()
else:
    from tests.test import test
    from tests.statement import lTest

    test(lTest, CStatement(), 'test_statement.tpl', 'statement')
    print "All test passed."
