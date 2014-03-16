import sys
from pyrser import meta, parsing


@meta.decorator("trace")
class Trace(parsing.DecoratorWrapper):

    def __init__(self, outfile: str=""):
        self.level = 0
        self.indent = 4
        if outfile != "":
            self.out = open(outfile, 'w')
        else:
            self.out = sys.stdout

    def __destroy__(self):
        self.out.close()

    def begin(self, parser: parsing.BasicParser, pt: parsing.Functor):
        """
        The begin method of the "root" Trace has to open the output
        for all its children tracers.
        """
        item = pt
        while isinstance(item, parsing.Directive) or
        isinstance(item, parsing.Decorator):
            item = item.pt

        if isinstance(item, parsing.Rule) is False:
            self.out.write(" " * self.indent * self.level
                           + "[" + item.name + "] Entering\n")
            self.level += 1

        return True

    def end(self,
            result: bool, parser: parsing.BasicParser, pt: parsing.Functor):
        """
        The end method of the "root" Trace has to close the output
        """

        item = pt
        while isinstance(item, parsing.Directive) or
        isinstance(item, parsing.Decorator):
            item = item.pt

        if isinstance(item, parsing.Rule) is False:
            self.level -= 1
            rstr = "Failed"
            if result is not False:
                rstr = "Succeeded"
            self.out.write(" " * self.indent * self.level
                           + "[" + item.name + "] " + rstr + "\n")

        return True
