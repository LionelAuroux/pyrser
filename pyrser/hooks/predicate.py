from pyrser import meta
from pyrser.parsing.base import BasicParser


@meta.hook(BasicParser, "false")
def pred_false(self):
    """
    False in parser. Go to alternative...

    example::

        R = [
            #false | R2
        ]

    """
    return False


@meta.hook(BasicParser, "true")
def pred_true(self):
    """
    True in parser. Do nothing

    example::

        R = [
            R2 | #true
        ]

    """
    return True


@meta.hook(BasicParser, "eq")
def pred_eq(self, n, val):
    """
    Test if a node set with setint or setstr equal a certain value

    example::

        R = [
            __scope__:n
            ['a' #setint(n, 12) | 'b' #setint(n, 14)]
            C
            [#eq(n, 12) D]
        ]

    """
    v1 = n.value
    v2 = val
    if hasattr(val, 'value'):
        v2 = val.value
    if isinstance(v1, int) and not isinstance(v2, int):
        return v1 == int(v2)
    return v1 == v2


@meta.hook(BasicParser, "neq")
def pred_neq(self, n, val):
    """
    Test if a node set with setint or setstr not equal a certain value

    example::

        R = [
            __scope__:n
            ['a' #setint(n, 12) | 'b' #setint(n, 14)]
            C
            [#neq(n, 12) D]
        ]

    """
    v1 = n.value
    v2 = val
    if hasattr(val, 'value'):
        v2 = val.value
    if isinstance(v1, int) and not isinstance(v2, int):
        return v1 != int(v2)
    return v1 != v2
