from pyrser import meta, parsing


@meta.directive("ignore")
class Ignore(parsing.DirectiveWrapper):
    def begin(self, parser, convention: str):
        if convention == "null":
            parser.push_ignore(parsing.Parser.ignore_null)
        return True

    def end(self, parser, convention: str):
        parser.pop_ignore()
        return True
