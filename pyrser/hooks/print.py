from pyrser import meta
from pyrser.parsing.parserBase import BasicParser


@meta.hook(BasicParser, "print")
def print_nodes(self, *rest):
    """
        Print nodes

        example:

            R ::=
                In : node #print(node)
            ;

    """
    print(*rest)
    return True
