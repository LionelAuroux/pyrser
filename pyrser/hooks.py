from pyrser.node import next, next_is, clean_tree, slide, next_clean
from pyrser.parsing import Parsing
from pyrser.trace import *
from pprint import pprint

class GenericHook(object):
##### Hooks:
      def trueHook(self, oNode):
          """
	  #true :
	  Returns True.
	  Usefull for debug, for example if you didn't developp a part of a grammar.
	  """
          return True

      def falseHook(self, oNode):
          """
	  #false :
	  Returns False.
	  Usefull for debug, for example if you didn't developp a part of a grammar.
	  """
          return False

      def dumpHook(self, oNode):
	  """
	  #dump :
	  Dump the content of the current node.
	  """
	  pprint(oNode)
          return True

      def printHook(self, oNode, sStr):
          """
	  #print(sStr) :
	  Print sStr.
	  """
	  print sStr
          return True

      def idHook(self, oNode, sName):
          """
	  #id :
	  Print id of the local oNode.
	  """
          print "[%s] - %s" % (sName, id(oNode))
	  return True

      def exitHook(self, oNode):
          """
	  #exit :
	  Exit the processus.
	  """
          exit(1)

      def traceHook(self, oNode):
	  """
	  Trace the function called until now.
	  """
	  rule_stack_trace(self)
	  return True

      def slideHook(self, oNode, sField, sSubKey = None):
	  """
	  #slide(sField) :
	  The whole content of oNode will be put in a new node, stored at sField.
	  """
	  if sSubKey != None:
	    oNode = oNode[sSubKey]
	  slide(oNode, sField)
	  return True


##### Wrappers:
      def _Wrapper(self, oRule, oNode):
	  """
	  @_ :
	  The next node used as local for the following rules will be the
	  current local node.
	  """
	  next_is(oNode, oNode)
	  bRes = oRule()
	  next_clean(oNode)
	  return bRes

      def nextWrapper(self, oRule, oNode, sField, bClean = False):
	  """
	  @next(sField) :
	  The next node used as local for the following rules is created and
	  added under the sField key.
	  If the oRule wrapped fails the node will be delete.
	  """
	  next(oNode, sField)
	  bRes = oRule()
	  if bClean == True\
	    and bRes == False:
	    del oNode[sField]
	  next_clean(oNode)
          return bRes

      def push_atWrapper(self, oRule, oNode, sField):
	  """
	  @push_at(sField) :
	  The next node used as local is created and add to a list, at sField
	  if oRule succeed.
	  """
	  oSub = {}
	  next_is(oNode, oSub)
	  bRes = oRule()

	  if bRes == True:
	    if not oNode.has_key(sField):
	      oNode[sField] = []
	    oNode[sField].append(oSub)

	  next_clean(oNode)
          return bRes

      def push_capture_atWrapper(self, oRule, oNode, sField, sCapture):
          """
	  @push_capture_at(sField, sCapture) :
	  If the wrapped oRule succeeds the captured text stored at sCapture key will
	  be push at the sField list.
	  """
	  next_is(oNode, oNode)
	  bRes = oRule()

	  if bRes == True\
	    and oNode.has_key(sCapture):
	    if not oNode.has_key(sField):
	      oNode[sField] = []
	    oNode[sField].append(oNode[sCapture])
	    del oNode[sCapture]

	  next_clean(oNode)
          return bRes

      def slideWrapper(self, oRule, oNode, sField, sSubKey = None):
	  """
	  @slide(sField) :
	  If the oRule succeed, the whole content of oNode will be put in a new
	  node, stored at sField.
	  """
	  bRes = oRule()
	  if bRes == True:
	    if sSubKey != None:
	      oNode = oNode[sSubKey]
	    slide(oNode, sField)
	  return bRes

      def continueWrapper(self, oRule, oNode, sText = None):
          """
	  @continue(sText?) :
	  This wrapper should be used to keep trace of errors.
	  If the wrapped oRule fail, an execution stack will be printed ,an
	  Exception raised and the processus will be exit.
	  """
	  oTrace = set_stack_trace(self)
	  bRes = oRule()
	  if bRes == False:
	    result_stack_trace(oTrace)
    	    if sText != None:
	      raise Exception(sText)
	      exit(1)
	    raise Exception
	    exit(1)
          return bRes

      def traceWrapper(self, oRule, oNode, sName):
          """
	  @trace(sText?) :
	  Print the rules, hooks and wrappers called by oRule, and their result.
	  """
	  oTrace = set_stack_trace(self)
	  bRes = oRule()
	  result_stack_trace(oTrace)
	  return bRes

      def consumedWrapper(self, oRule, oNode, sName):
          """
	  @consumed(sName) :
	  Will display the text consumed by oRule if it succeeds.
	  """
	  Parsing.oBaseParser.setTag(sName)
	  bRes = oRule()
	  if bRes == True:
	    print "Consumed [%s] - %s" % (sName, Parsing.oBaseParser.getTag(sName))
          return bRes
