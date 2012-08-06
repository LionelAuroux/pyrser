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

from parsing.parsing_context import parsingContext
from ast.node import next_is
from dsl_parser.dsl_parser import *

from imp import load_source
from os import getcwd

# FIXME : virer l'importation fixe du generateur
from code_generation.python import *
from time import time

class Grammar(object):
      """
      This class turn any class A that inherit it into a grammar.
      Taking the description of the grammar in parameter it will add
      all what is what is needed for A to parse it.
      """

      @classmethod
      def __compile_grammar(oCls,
	  oSon, sSource, dGlobals,
	  bFromString,
	  sOutFile, sLang):

	  sCurrentFile = oSon.__name__
	  if bFromString == False:
	    sCurrentFile = sSource
	    sSource = fileChecking(sSource, bFromString, parse)

          oGrammarAst = parse(sSource, {}, oSon.__name__)

	  # FIXME : path non absolu
	  sPath = '%s/pyrser/lang/%s/%s.py' % (getcwd(), sLang, sLang)
	  oLangModule = load_source(sLang, sPath)

	  dLangConf = getattr(oLangModule, sLang)
	  
	  # FIXME : choper la bonne classe : python/c/c++/ocaml etc
#	  t = time()
	  sGeneratedCode =\
	      Python(dLangConf).translation(oSon.__name__, oGrammarAst['rules'])
#	  print time() - t

#	  print sGeneratedCode
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

	  oSon.bIsSet = True
	  # FIXME : try/catch to test if a PostGeneration function was defined
#	  return getattr(oLangModule, '%sPostGeneration' % sLang)\
#	      (sModuleName, sOutFile, sToFile, sGrammar, self)

      def __init__(self,
	  sName, sSource, dGlobals = None,
	  bFromString = True,
	  sOutFile = None, sLang = 'python'):
	  self.__compile_grammar(
	      sName, sSource, dGlobals, bFromString, sOutFile, sLang)

      def parse(self, sSource, oRoot, sRuleName):
	  next_is(oRoot, oRoot)
	  Parsing.oBaseParser.parsedStream(sSource)
	  if hasattr(self, '%sRule' % sRuleName) == False:
	    raise Exception('First rule doesn\'t exist : %s' % sRuleName)
	  if getattr(self, '%sRule' % sRuleName)(oRoot) == False:
	    return False
	  Parsing.oBaseParser.readWs()
	  return Parsing.oBaseParser.readEOF()

      def __getattr__(self, sName):
	  if sName.endswith('Rule'):
	    raise Exception('No such rule declared : %s::%s'\
			    % (self.__class__.__name__, sName))
          raise AttributeError, sName
