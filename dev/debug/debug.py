from pyrser.grammar import Grammar
from pyrser.hooks import GenericHook


class CExpression(Grammar):
    """
    expression ::= '1'
    ;

    constant ::= '1'
    ;
    """
    __metaclass__ = Singleton

    def __init__(self):
        Grammar.__init__(self, CExpression,
                         CExpression.__doc__,
                         globals())


class CStatement(GenericHook, Grammar):
    """
/* vim: set filetype=ocaml : */

statement ::=
    @trace('debug')
    [
     @_
     [
        selection
      | compound
      | iteration
      | jump
      | labeled
      | expression
     ]
     ]
;

selection ::=
       [
         "if" :keyword '('  @next("condition") CExpression::expression ')'
         @next("stmt") statement
         [ "else"  @next("else") statement]?
       |
         "switch" :keyword '('  @next("condition") CExpression::expression ')'
         @next("stmt") statement
       ]
       #type("selection")
;

compound ::=
       '{'

       [@push_at("stmts") statement ]*
       #type("compound")

       '}'
;

iteration ::=
       [
         "while" :keyword '('  @next("condition") CExpression::expression ')'
         @next("stmt") statement
       |
         "do" :keyword
         @next("stmt") statement
         "while" '('  @next("condition") CExpression::expression ')' ';'
       |
         "for" :keyword '('
         @next("for_init") [CExpression::expression]? ';'
         @next("condition") [CExpression::expression]? ';'
         @next("for_each")  [CExpression::expression]? ')'
         @next("stmt") statement
       ]
       #type("iteration")
;

jump ::=
       [
         "goto" :keyword #identifier :label ';'
       |
         ["continue" | "break"] :keyword ';'
       |
         "return" :keyword '(' @next("condition")
         [CExpression::expression]? ");"
       ]
        #type("jump")
;

labeled ::=
      [
        [
            "default" :keyword
          | "case" :keyword #false CExpression::constant
          | #identifier :label
        ]
        ':' @next("stmt") statement
      ]
      #type("labeled")
;

expression ::=
       @next("subexpr") [CExpression::expression]? ';'
       #type("expression")
;
    """
    __metaclass__ = Singleton

    def __init__(self):
        GenericHook.__init__(self)
        Grammar.__init__(self, CStatement,
                         CStatement.__doc__,
                         globals())

    def typeHook(self, oNode, sSubExpr, sType="__statement__"):
        """
        Type should attribute an automatic name: per grammar function.
        """
        oNode["type"] = "stmt"
        oNode["sub_type"] = sSubExpr
        return oNode

    def hereHook(self, oNode):
        print "HERE"
        return True

if __name__ == '__main__':
# FIXME : segmentation fault
# 0   asciiParse.so   0x0000000106076d08 AsciiParse::readIgnored() const + 20
    oRoot = {}
    print CStatement().parse('if (1)\n{\n}', oRoot, 'statement')
    print Grammar.nCount
