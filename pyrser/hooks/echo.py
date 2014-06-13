from pyrser import meta
from pyrser.parsing import Node
from pyrser.parsing.base import BasicParser


@meta.hook(BasicParser, "echo")
def echo_nodes(self, *rest):
    """
    Print nodes.

    example::

        R = [
            In : node #echo("coucou", 12, node)
        ]

    """
    txt = ""
    for thing in rest:
        if isinstance(thing, Node):
            txt += self.value(thing)
        else:
            txt += str(thing)
    print(txt)
    return True
