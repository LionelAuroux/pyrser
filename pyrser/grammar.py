# Copyright (C) 2012 Candiotti Adrien 
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# 
# See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
from imp import load_source
from traceback import extract_tb

from parsing.parsing_context import parsingContext
from node import next_is
from dsl_parser.dsl_parser import *


# FIXME : virer l'importation fixe du generateur
from code_generation.python import *
# FIXME : solution provisoire
from os import getenv
# FIXME : debug
from time import time
# ENDFIXME

def runtime_error_handle(oType, oValue, oTraceback):
    lCalls = extract_tb(oTraceback)
    print "Fatal error : %s %s" % (oType, oValue)
    print "This is a traceback of the called rules, hooks and wrappers:"
    nDepth = 1
    for iCall in lCalls:
      for iManglingEnd in ['Rule', 'Wrapper', 'Hook']:
        if iCall[2].endswith(iManglingEnd):
          sFile = iCall[0]
          if sFile == '<string>':
            sFile = 'generated grammar'
          print "%s+|In %s line %s: %s (%s)" %\
                    (nDepth * '-',
                     sFile,
                     iCall[1],
        	     iCall[2][:-len(iManglingEnd)],
        	     iManglingEnd)
          if iManglingEnd == 'Rule':
            nDepth += 1
    exit(1)

#sys.excepthook = runtime_error_handle

class Grammar(object):
      """
      This class turn any class A that inherit it into a grammar.
      Taking the description of the grammar in parameter it will add
      all what is what is needed for A to parse it.
      """

      # FIXME : instanciation's debug
      nCount = 0
      # ENDFIXME

      TRACE = False
      # Borg design pattern.
      dDefined = {}

      @classmethod
      def __compile_grammar(oCls,
          oSon, sSource, dGlobals,
          bFromString,
          sOutFile, sLang):

          sCurrentFile = oSon.__name__
          if bFromString == False:
            sCurrentFile = sSource
            # FIXME : fileChecking n'existe plus, trouver une solution generique
            sSource = fileChecking(sSource, bFromString, parse)

          oGrammarAst = parse(sSource, {}, oSon.__name__)
          Grammar.nCount += 1

          # FIXME : path non absolu
          # DEBUG:
          if getenv('PYRSERPATH') == None:
            raise Exception('Set PYRSERPATH in the environment.')
          # ENDFIXME
          sPath = '%s/pyrser/lang/%s/%s.py' % (getenv('PYRSERPATH'), sLang, sLang)
          oLangModule = load_source(sLang, sPath)

          dLangConf = getattr(oLangModule, sLang)
          
          # FIXME : choper la bonne classe : python/c/c++/ocaml etc
#          t = time()
          sGeneratedCode =\
              Python(dLangConf).translation(oSon.__name__, oGrammarAst['rules'])
#          print time() - t

#          print sGeneratedCode
          oByteCode = compile(sGeneratedCode, "<string>", "exec")
  
          if dGlobals == None:
            dGlobals = globals()
          else:
            dGlobals.update(globals())

          eval(oByteCode, dGlobals, locals())

          dLocals = locals()
          for iKey, iValue in dLocals['CompiledGrammar'].__dict__.iteritems():
            if hasattr(iValue, '__func__'):
              setattr(oCls, iKey, getattr(dLocals['CompiledGrammar'], iKey))

          # FIXME : try/catch to test if a PostGeneration function was defined
#          return getattr(oLangModule, '%sPostGeneration' % sLang)\
#              (sModuleName, sOutFile, sToFile, sGrammar, self)

      def __init__(self,
          oSon, sSource, dGlobals = None,
          bFromString = True,
          sOutFile = None, sLang = 'python'):
          sName = oSon.__name__
          if sName not in Grammar.dDefined:
            self.__compile_grammar(
        	oSon, sSource, dGlobals, bFromString, sOutFile, sLang)
            Grammar.dDefined[sName] = oSon

      def parse(self, sSource, oRoot, sRuleName):
          next_is(oRoot, oRoot)
          Parsing.oBaseParser.parsedStream(sSource)
          if hasattr(self, '%sRule' % sRuleName) == False:
            raise Exception('First rule doesn\'t exist : %s' % sRuleName)
          bRes = getattr(self, '%sRule' % sRuleName)(oRoot)
          if not bRes:
            return False
          Parsing.oBaseParser.readWs()
          return Parsing.oBaseParser.readEOF()

      def __getattr__(self, sName):
          for iManglingEnd in ['Rule', 'Hook', 'Wrapper']:
            if sName.endswith(iManglingEnd):
              raise Exception('No such %s declared : %s::%s'\
        	% (iManglingEnd.lower(),
        	  self.__class__.__name__,
        	  sName[:-len(iManglingEnd)]))
          raise AttributeError, sName
