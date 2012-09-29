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
		"type" : "__primary__",
		"sign" : "signed",
		"type_specifier" : "int",
		"type_qualifier" : None,
		"storage_class_specifier" : "auto"
	      }

      def typeHook(self, oNode, sSubExpr, sType = "__declaration__"):
	  """
	  Type should attribute an automatic name: per grammar function.
	  """
	  oNode["type"] = sType
	  oNode["sub_type"] = sSubExpr
          return oNode

      def setHook(self, oNode, sKey, sValue, sSubKey = None):
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

      def cleanHook(self, oNode, sKey, sSubKey = None):
	  if sSubKey != None\
	    and oNode.has_key(sSubKey):
	    oNode = oNode[sSubKey]
	  if oNode.has_key(sKey):
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
	  if not oNode.has_key("ctype"):
	    oNode["ctype"] = copy(self.__dDefaultCType)
	  else:
	    for iKey, iValue in self.__dDefaultCType.iteritems():
	      if not oNode["ctype"].has_key(iKey):
		oNode["ctype"][iKey] = iValue
          return True

      def insert_ptrHook(self, oNode):
	  self.cdeclHook(oNode)
	  if oNode["ctype"].has_key("pointer") == False:
	    oNode["ctype"]["pointer"] = []
	  oNode["ctype"]["pointer"].append({})
          return True

      def add_qualifierHook(self, oNode):
	  oNode["ctype"]["pointer"][-1]["type_qualifier"] = oNode["type_qualifier"]
	  del oNode["type_qualifier"]
          return True

      def composed_type_rewriteHook(self, oNode):
	  if oNode["ctype"].has_key("sub_type"):
	    oNode["ctype"]["type"] = oNode["ctype"]["sub_type"]
	    del oNode["ctype"]["sub_type"]
          return True

      def func_ptr_or_prototypeHook(self, oNode):
	  if oNode["ctype"].has_key("pointer")\
	    and oNode["ctype"].has_key("return"):
	    self.ctypeHook(oNode, "__func_ptr__")
	    self.typeHook(oNode, "__declaration__")
	  #elif oNode["ctype"].has_key('params')\
	  elif not oNode.has_key('array')\
	    and not oNode.has_key('body')\
	    and oNode["ctype"]["type"] not in\
	    ["__union__", "__enum__", "__struct__"]:
	    self.typeHook(oNode, "__prototype__")
	    if oNode["ctype"].has_key("return"):
	      oNode["ctype"].update(oNode["ctype"]["return"])
	      del oNode["ctype"]["return"]
	  if oNode["ctype"]["type"] == "declaration_specifiers":
	    self.ctypeHook(oNode, "__variable__")
          return True

      def isHook(self, oNode, sType, sSubKey = None):
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
