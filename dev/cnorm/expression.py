from pyrser.grammar import Grammar
from pyrser.hooks import GenericHook
from pyrser.node import slide, next


class CExpression(GenericHook, Grammar):
    def __init__(self):
        GenericHook.__init__(self)
        Grammar.__init__(self, CExpression,
                         open("./grammar/expression.pw").read(),
                         globals())

    def __type(self, oNode, sSubExpr, sType="__expression__"):
        """
        Type should attribute an automatic name: per grammar function.
        """
        oNode["type"] = sType
        oNode["sub_type"] = sSubExpr
        return oNode

    def to_post_exprHook(self, oNode, sType):
        if "postfix" not in oNode:
            oNode["postfix"] = []
        oIndex = {"expr": {}}
        self.__type(oIndex, sType)
        oNode["postfix"].append(oIndex)
        next_is(oNode, oNode["postfix"][-1]["expr"])
        return True

    def type_nextHook(self, oNode, sSubType, sNext):
        next(oNode, sNext)
        self.__type(oNode, sSubType)
        return True

    def Nnary_opHook(self, oNode, sSubType, sSide, sNext):
        slide(oNode, sSide)
        self.__type(oNode, sSubType)
        next(oNode, sNext)
        return True

    def primaryHook(self, oNode, sOperator):
        self.__type(oNode, "terminal")
        oNode["operator"] = sOperator
        return True

    def to_post_opHook(self, oNode, sType):
        self.to_post_exprHook(oNode, sType)
        oNode["postfix"][-1]["expr"]["op"] = oNode["op"]
        del oNode['op']
        return True

    def sizeofHook(self, oNode):
        if "primary_id" in oNode\
                and oNode["primary_id"] == "sizeof":
            oExpr = oNode["postfix"][0]["expr"]
            oNode.clear()
            self.__type(oNode, "sizeof")
            oNode["expr"] = oExpr
        return True

    def captured_somethingHook(self, oNode):
        # FIXME : workaround degueu car dans certains cas
        #	    la grammaire d'expression capture .. du vide
        bRes = len(oNode['captured']) > 0
        del oNode['captured']
        return bRes

if __name__ != '__main__':
    CExpression()
else:
    from tests.test import test
    from tests.expression import lTest

    test(lTest, CExpression(), 'test_expression.tpl', 'expression')
    print "All test passed."
