from pyrser.ast.node import next, next_is, clean_tree, slide, next_clean
from pyrser.parsing import Parsing
from pprint import pprint
from sys import settrace

class GenericHook(object):
      def __rule_stack_trace(self):
          """
	  Trace the rules, hook and wrapper calls.
	  """
	  nDepth = 1
	  for iCall in extract_stack():
	    for iManglingEnd in ['Rule', 'Wrapper', 'Hook']:
	      if iCall[2].endswith(iManglingEnd):
		sFile = iCall[0]
		if sFile == '<string>':
		  sFile = 'generated grammar'
	        print "%s+|In %s line %s: %s::%s" %\
	            (nDepth * '-',
	             sFile,
	             iCall[1],
	             self.__class__.__name__,
	             iCall[2])
	        if iManglingEnd == 'Rule':
	          nDepth += 1
      
      def __set_stack_trace(self):
	  oTrace = self.__Trace(self)
	  settrace(oTrace)
	  return oTrace

      def __result_stack_trace(self, oTrace):
          """
	  Trace the rules, hook and wrapper calls with their result.
	  """
          settrace(lambda x, y, z : None)
	  for iCall in oTrace.lCalled:
	    sFile = iCall['file']
	    if sFile == '<string>':
	      sFile = 'generated grammar'
	    print "%s+|In %s line %s: %s::%s => [%s]"\
		% (iCall['depth'] * '-'
		  ,sFile
		  ,iCall['line']
		  ,iCall['grammar']
		  ,iCall['name']
		  ,iCall['return'])

      class __Trace(object):
	    def __init__(self, oGrammar):
	        self.lCalled = []
		self.nDepth = 1
		self.sGrammarName = oGrammar.__class__.__name__
	          
	    def __call__(self, oFrame, sEvent, oArg):
		sFuncName = oFrame.f_code.co_name
		if sFuncName.endswith('Rule')\
		      or sFuncName.endswith('Wrapper')\
		      or sFuncName.endswith('Hook'):
		  if sEvent == 'call':
		    self.lCalled.append({'name' : sFuncName
					,'depth' : self.nDepth
					,'grammar' : self.sGrammarName
					,'line' : oFrame.f_lineno
					,'file' : oFrame.f_code.co_filename})
		    self.nDepth += 1
		  elif sEvent == 'return':
		    nCount = len(self.lCalled) - 1
		    while nCount >= 0:
		      if self.lCalled[nCount]['name'] == sFuncName:
			self.lCalled[nCount]['return'] = oArg
		      nCount -= 1
		    self.nDepth -= 1
		return self.__call__

##### Hooks:
      def trueHook(self, oNode):
          """
	  #true :
	  Returns True.
	  Usefull for debug, for example if you didn't developp a part of a grammar.
	  """
          return True

      def FalseHook(self, oNode):
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
	  self.__rule_stack_trace()
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

      def nextWrapper(self, oRule, oNode, sField):
	  """
	  @next(sField) :
	  The next node used as local for the following rules is created and
	  added under the sField key.
	  If the oRule wrapped fails the node will be delete.
	  """
	  next(oNode, sField)
	  bRes = oRule()
	  if bRes == False:
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

      def slideWrapper(self, oRule, oNode, sField):
	  """
	  @slide(sField) :
	  If the oRule succeed, the whole content of oNode will be put in a new
	  node, stored at sField.
	  """
	  bRes = oRule()
	  if bRes == True:
	    slide(oNode, sField)
	  return bRes

      def continueWrapper(self, oRule, oNode, sText = None):
          """
	  @continue(sText?) :
	  This wrapper should be used to keep trace of errors.
	  If the wrapped oRule fail, an execution stack will be printed ,an
	  Exception raised and the processus will be exit.
	  """
	  oTrace = self.__set_stack_trace
	  bRes = oRule()
	  if bRes == False:
	    self.__result_stack_trace(oTrace)
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
	  oTrace = self.__set_stack_trace()
	  bRes = oRule()
	  self.__result_stack_trace(oTrace)
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
