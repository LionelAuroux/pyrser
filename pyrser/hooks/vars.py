from pyrser import meta
from pyrser.parsing import Node
from pyrser.parsing.base import BasicParser


@meta.hook(BasicParser, "vars")
def vars_nodes(self, rest):
    """
    Vars one node instance.

    example::

        R = [
            In : node #vars(node)
        ]

    """
    print(vars(rest))
    return True
