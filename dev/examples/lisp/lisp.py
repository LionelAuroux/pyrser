from pyrser.grammar import Grammar
from pyrser.parsing import resetBaseParser
from pyrser.hooks import GenericHook
from pyrser.node import *

class Lisp(GenericHook, Grammar):
      """
      s_expression ::= 	 @_ atomic_symbol 
	               | @_ list #type("list")
      ;

      list ::=	'(' 
		    @push_at("list") s_expression #func_call
		  [ @push_at("list") s_expression ]*
		')'
		#sub_type("list")
      ;

      atomic_symbol ::= [  
			    #identifier  :symbol #sub_type("identifier")
			  | #num  :symbol #sub_type("integer")
			  | #string :symbol #sub_type("string")
			  | 
			  [
			    [ '+' | '-' | '*' | '/' | '%' ]
			    |
			    [ "<=" | ">=" | '<' | '>' | '=' | "!="]
			    |
			    [ '!' | "&&" | '|']
			  ]
			    #sub_type("operator")
			] :symbol
			#type("atom")
      ;

      """
      def __init__(self):
          super(Lisp, self).__init__(Lisp, Lisp.__doc__, globals())
	  resetBaseParser("", " \r\n\t", ";") # FIXME : don't work

      def sub_typeHook(self, oNode, sSubtype):
	  oNode['sub_type'] = sSubtype
          return True

      def typeHook(self, oNode, sType):
	  oNode['type'] = sType
          return True

      def func_callHook(self, oNode):
	  if oNode["list"][0]["type"] == "atom"\
	    and oNode["list"][0]["sub_type"] == "identifier":
	    oNode["list"][0]["sub_type"] = "functor"
          return True

oRoot = {}
sTest = '(let ((x 20) (y 22)) (+ x y))'
#sTest = '(add 1 3)'
print sTest
print Lisp().parse(sTest, oRoot, 's_expression')
clean_tree(oRoot, 'parent')
from pprint import pprint
pprint(oRoot)


dOperatorTable =\
    {
      '+' : 'add',
      '-' : 'minus',
      '*' : 'time',
      '/' : 'divide',
      '%' : 'modulus',
      '>' : 'greater',
      '<' : 'less',
      '=' : 'equal',
      ">=" : 'greater_or_equal',
      "<=" : 'less_or_equal',
      "!=" : 'different',
    }

nListDepth = 0

def list(oNode, nCount):
    global nListDepth
    sRes = "\n%s" % (nListDepth * ' ')
    if nCount > 0:
      sRes += ","
    else:
      sRes += " "
    if nListDepth > 0:
      if oNode['list'][0]['sub_type'] == "list":
	sRes += "list"
      else:
	sRes += "functor"
    nListDepth += 1
    sRes += "("
    nLocalCount = 0
    for iBranch in oNode['list']:
      sRes += globals()[iBranch['type']](iBranch, nLocalCount)
      nLocalCount += 1
    sRes += ")"
    nListDepth -= 1
    return sRes

def atom(oNode, nCount):
    sRes = ""
    if nCount > 0:
      sRes += " ,"
    if oNode['sub_type'] != "operator":
      if oNode['sub_type'] != 'functor':
	sRes += "%s(%s)" % (oNode['sub_type'], oNode['symbol'])
      else:
	sRes += "%s" % (oNode['symbol'])
    else:
      sRes += dOperatorTable[oNode['symbol']]
    return sRes

print "exec_functor(functor%s)" % list(oRoot, 0)
