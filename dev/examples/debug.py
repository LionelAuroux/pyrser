from pyrser import Grammar
from pyrser.hooks import GenericHook
from pyrser.node import clean_tree
from pprint import pprint


class Debug(Grammar, GenericHook):
    """
    debug ::= @next("sub") sub
    ;

    sub ::= @_ [subsub | foo]
    ;

    subsub ::= #identifier :id
    ;

    foo ::= #num :num
    ;
    """
    def __init__(self):
        Grammar.__init__(self, Debug, Debug.__doc__)
        GenericHook.__init__(self)

oGrammar = Debug()
oRoot = {}
print oGrammar.parse('123', oRoot, 'debug')
clean_tree(oRoot, 'parent')
clean_tree(oRoot, 'type')
pprint(oRoot)
