from pyrser import meta
from pyrser.parsing import Node
from pyrser.parsing.base import BasicParser


@meta.hook(BasicParser, "set")
def set_node(self, dst, src):
    """
        Basically copy one node to another.
        usefull to transmit a node from a terminal
        rule as result of the current rule.

        example::

            R = [
                In : node #set(_, node)
            ]

        here the node return by the rule In is
        also the node return by the rule R
    """
    if not isinstance(src, Node):
        dst.value = src
    else:
        dst.set(src)
    return True
