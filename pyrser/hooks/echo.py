from pyrser import meta
from pyrser.parsing.parserBase import BasicParser


@meta.hook(BasicParser, "echo")
def echo_nodes(self, *rest):
    """
    Print nodes

    example:

        R ::=
            In : node #echo(node)
        ;
    """
    print(*rest)
    return True

