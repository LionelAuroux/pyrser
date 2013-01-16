from pyrser.grammar import Grammar
from pyrser.hooks import GenericHook
from expression import CExpression
from statement import CStatement
from copy import copy


class CDeclaration(GenericHook, Grammar):
    def __init__(self):
        GenericHook.__init__(self)
        Grammar.__init__(self, CDeclaration,
                         open("./grammar/declaration.pw").read(),
                         globals())
        self.__dDefaultCType =\
            {
                "type": "__primary__",
                "sign": "signed",
                "type_specifier": "int",
                "type_qualifier": None,
                "storage_class_specifier": "auto"
            }

    def typeHook(self, oNode, sSubExpr, sType="__declaration__"):
        """
        Type should attribute an automatic name: per grammar function.
        """
        oNode["type"] = sType
        oNode["sub_type"] = sSubExpr
        return oNode

    def setHook(self, oNode, sKey, sValue, sSubKey=None):
        if sSubKey != None:
            oNode = oNode[sSubKey]
        oNode[sKey] = sValue
        return True

    def ctypeHook(self, oNode, sCType):
        oNode["ctype"]["type"] = sCType
        return True

    def resetHook(self, oNode):
        oNode.clear()
        return True

    def cleanHook(self, oNode, sKey, sSubKey=None):
        if sSubKey != None\
                and sSubKey in oNode:
            oNode = oNode[sSubKey]
        if sKey in oNode:
            del oNode[sKey]
        return True

    def push_rootHook(self, oNode, sField):
        oRoot = self.root()
        oRoot[sField].append(copy(oNode))
        next_is(oNode, oRoot[sField][-1])
        return True

    def push_parentHook(self, oNode, sField):
        # FIXME : solve the parent referencing problem
        return True
        oParent = oNode['parent']
        oParent[sField].append(copy(oNode))
        next_is(oNode, oParent[sField][-1])
        return True

    def cdeclHook(self, oNode):
        if "ctype" not in oNode:
            oNode["ctype"] = copy(self.__dDefaultCType)
        else:
            for iKey, iValue in self.__dDefaultCType.iteritems():
                if iKey not in oNode["ctype"]:
                    oNode["ctype"][iKey] = iValue
        return True

    def insert_ptrHook(self, oNode):
        self.cdeclHook(oNode)
        if ("pointer" in oNode["ctype"]) == False:
            oNode["ctype"]["pointer"] = []
        oNode["ctype"]["pointer"].append({})
        return True

    def add_qualifierHook(self, oNode):
        oNode["ctype"]["pointer"][-1]["type_qualifier"] = oNode[
            "type_qualifier"]
        del oNode["type_qualifier"]
        return True

    def composed_type_rewriteHook(self, oNode):
        if "sub_type" in oNode["ctype"]:
            oNode["ctype"]["type"] = oNode["ctype"]["sub_type"]
            del oNode["ctype"]["sub_type"]
        return True

    def func_ptr_or_prototypeHook(self, oNode):
        if "pointer" in oNode["ctype"]\
                and "return" in oNode["ctype"]:
            self.ctypeHook(oNode, "__func_ptr__")
            self.typeHook(oNode, "__declaration__")
        # elif oNode["ctype"].has_key('params')\
        elif 'array' not in oNode\
            and 'body' not in oNode\
            and oNode["ctype"]["type"] not in\
                ["__union__", "__enum__", "__struct__"]:
            self.typeHook(oNode, "__prototype__")
            if "return" in oNode["ctype"]:
                oNode["ctype"].update(oNode["ctype"]["return"])
                del oNode["ctype"]["return"]
        if oNode["ctype"]["type"] == "declaration_specifiers":
            self.ctypeHook(oNode, "__variable__")
        return True

    def isHook(self, oNode, sType, sSubKey=None):
        if sSubKey != None:
            oNode = oNode[sSubKey]
        print oNode['type']
        return oNode['type'] == sType


if __name__ != '__main__':
    CDeclaration()
else:
    from tests.test import test
    from tests.declaration import lTest

    bRes = test(lTest, CDeclaration(), 'declaration.tpl', 'translation_unit')
    if bRes == False:
        print "All test passed."
    else:
        print "Some exceptions were raised in the hooks."
