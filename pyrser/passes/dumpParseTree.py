# This pass is for debug only
from pyrser import meta
from pyrser import parsing


@meta.add_method(parsing.Parser)
def dumpParseTree(self):
    res = ""
    for k, v in self.__class__._rules.items():
        if isinstance(v, parsing.ParserTree):
            res += "\n\t{} ::= {}\t;".format(k, v.dumpParseTree(1))
        else:
            res += "\n\t{} ::= {};".format(k, repr(v))
    return res


def _dumpParam(pt):
    res = ""
    if len(pt.param) > 0:
        lsparam = []
        for p in pt.param:
            if p[1] is str:
                lsparam.append('"' + p[0] + '"')
            else:
                lsparam.append(p[0])
        res = "({})".format(", ".join(lsparam))
    return res


@meta.add_method(parsing.Rule)
def dumpParseTree(self, level=0):
    return "{}{}".format('\t' * level, self.name)


@meta.add_method(parsing.Hook)
def dumpParseTree(self, level=0):
    return "{}#{}{}".format('\t' * level, self.name, _dumpParam(self))


@meta.add_method(parsing.Call)
def dumpParseTree(self, level=0):
    #TODO(iopi): think to remap methods to hooks
    if self.callObject == parsing.Parser.read_range:
        return "{}'{}'..'{}'".format(
            '\t' * level, self.params[0], self.params[1])
    elif self.callObject == parsing.Parser.read_char:
        return "{}'{}'".format('\t' * level, self.params[0])
    elif self.callObject == parsing.Parser.read_text:
        return "{}\"{}\"".format('\t' * level, self.params[0])
    elif self.callObject == parsing.Parser.read_integer:
        return "{}#num".format('\t' * level)
    elif self.callObject == parsing.Parser.read_identifier:
        return "{}#id".format('\t' * level)
    else:
        res = "{}#call: {} (".format('\t' * level, self.callObject.__name__)
        res += ", ".join(["{}".format(repr(param)) for param in self.params])
        res += ")"
        return res


@meta.add_method(parsing.Scope)
def dumpParseTree(self, level=0):
    res = "\n{}[{}\n".format('\t' * (level + 1), self.begin.dumpParseTree(0))
    res += self.pt.dumpParseTree(level + 1)
    res += "\n{}]{}\n".format('\t' * (level + 1), self.end.dumpParseTree(0))
    return res


@meta.add_method(parsing.Directive)
def dumpParseTree(self, level=0):
    # TODO: process parameter
    res = "\n{}@{}{}".format('\t' * (level + 1),
                             self.directive.ns_name,
                             _dumpParam(self))
    res += self.pt.dumpParseTree(level + 1)
    return res


@meta.add_method(parsing.Capture)
def dumpParseTree(self, level=0):
    res = "\n{}[\n".format('\t' * level)
    res += self.pt.dumpParseTree(level + 1)
    res += "\n{}] : {}\n".format('\t' * level, self.tagname)
    return res


@meta.add_method(parsing.Seq)
def dumpParseTree(self, level=0):
    return ' '.join([
        pt.dumpParseTree(level + 1) for pt in self.ptlist])


@meta.add_method(parsing.Alt)
def dumpParseTree(self, level=0):
    indent = '\t' * level
    res = "\n{}  {}".format(indent, self.ptlist[0].dumpParseTree(0))
    if len(self.ptlist) > 1:
        res += "\n{}| ".format(indent)
    res += "\n{}| ".format('\t' * level).join([
        pt.dumpParseTree(0) for pt in self.ptlist[1:]])
    return res


@meta.add_method(parsing.Neg)
def dumpParseTree(self, level=0):
    res = ("\n{}![\n".format('\t' * level))
    res += self.pt.dumpParseTree(level + 1)
    res += ("\n{}]\n".format('\t' * level))
    return res


@meta.add_method(parsing.Complement)
def dumpParseTree(self, level=0):
    res = ("\n{}~[\n".format('\t' * level))
    res += self.pt.dumpParseTree(level + 1)
    res += ("\n{}]\n".format('\t' * level))
    return res

@meta.add_method(parsing.Until)
def dumpParseTree(self, level=0):
    res = ("\n{}->[\n".format('\t' * level))
    res += self.pt.dumpParseTree(level + 1)
    res += ("\n{}]\n".format('\t' * level))
    return res


@meta.add_method(parsing.LookAhead)
def dumpParseTree(self, level=0):
    res = ("\n{}!![\n".format('\t' * level))
    res += self.pt.dumpParseTree(level + 1)
    res += ("\n{}]\n".format('\t' * level))
    return res


@meta.add_method(parsing.RepOptional)
def dumpParseTree(self, level=0):
    res = ("\n{}[\n".format('\t' * level))
    res += self.pt.dumpParseTree(level + 1)
    res += ("\n{}]?\n".format('\t' * level))
    return res


@meta.add_method(parsing.Rep0N)
def dumpParseTree(self, level=0):
    res = ("\n{}[\n".format('\t' * level))
    res += self.pt.dumpParseTree(level + 1)
    res += ("\n{}]*\n".format('\t' * level))
    return res


@meta.add_method(parsing.Rep1N)
def dumpParseTree(self, level=0):
    res = ("\n{}[\n".format('\t' * level))
    res += self.pt.dumpParseTree(level + 1)
    res += ("\n{}]+\n".format('\t' * level))
    return res
