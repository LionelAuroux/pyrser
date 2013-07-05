from pyrser import meta
from pyrser.parsing.parserBase import BasicParser


@meta.hook(BasicParser, "copy")
def copy_node(self, dst, src):
    """
        Basically copy one node to another

        usefull to transmit a node from a terminal
        rule as result of the current rule.

        example:

            R ::=
                In : node #copy(_, node)
            ;

        here the node return by the rule In is
        also the node return by the rule R
    """
    dst.set(src)
    return True
