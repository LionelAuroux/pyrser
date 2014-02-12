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
