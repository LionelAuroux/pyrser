# This pass is for debug only

from pyrser.meta import *
from pyrser.parsing.parserBase import *
import inspect


@add_method(BasicParser)
def dumpParseTree(self):
    res = "{"
    for k, v in self.rules.items():
        if isinstance(v, ParserTree):
            res += "\n\t{} : {}\t,".format(repr(k), v.dumpParseTree(1))
        else:
            res += "\n\t{} : {},".format(repr(k), repr(v))
    res += "\n}"
    return res


@add_method(Rule)
def dumpParseTree(self, level=0):
    return "{}{}".format('\t' * level, self.name)


@add_method(Hook)
def dumpParseTree(self, level=0):
    return "{}#{}".format('\t' * level, self.name)


@add_method(Call)
def dumpParseTree(self, level=0):
    #TODO(iopi): think to remap methods to hooks
    if self.callObject.__name__ == BasicParser.readRange.__name__:
        return ("{}'{}'..'{}'".format(
            '\t' * level,
            self.params[0],
            self.params[1]))
    elif self.callObject.__name__ == BasicParser.readChar.__name__:
        return ("{}'{}'".format('\t' * level, self.params[0]))
    elif self.callObject.__name__ == BasicParser.readText.__name__:
        return ("{}\"{}\"".format('\t' * level, self.params[0]))
    elif self.callObject.__name__ == BasicParser.readInteger.__name__:
        return ("{}#num".format('\t' * level))
    elif self.callObject.__name__ == BasicParser.readIdentifier.__name__:
        return ("{}#id".format('\t' * level))
    else:
        res = "{}#call: {} (".format('\t' * level, self.callObject.__name__)
        res += ", ".join(["{}".formt(repr(param)) for param in self.params])
        res += ")"
        return res


@add_method(Scope)
def dumpParseTree(self, level=0):
    res = "\n{}[{}\n".format('\t' * (level + 1), self.begin.dumpParseTree(0))
    res += self.clause.dumpParseTree(level + 1)
    res += "\n{}]{}\n".format('\t' * (level + 1), self.end.dumpParseTree(0))
    return res


@add_method(Capture)
def dumpParseTree(self, level=0):
    res = "\n{}[\n".format('\t' * level)
    res += self.clause.dumpParseTree(level + 1)
    res += "\n{}] : {}\n".format('\t' * level, self.tagname)
    return res


@add_method(Clauses)
def dumpParseTree(self, level=0):
    return ' '.join(
        [clause.dumpParseTree(level + 1) for clause in self.clauses])


@add_method(Alt)
def dumpParseTree(self, level=0):
    indent = '\t' * level
    res = "\n{}  {}".format(indent, self.clauses[0].dumpParseTree(0))
    if len(self.clauses) > 1:
        res += "\n{}| ".format(indent)
    res += "\n{}| ".format('\t' * level).join(
        [clause.dumpParseTree(0) for clause in self.clauses[1:]])
    return res


@add_method(RepOptional)
def dumpParseTree(self, level=0):
    res = ("\n{}[\n".format('\t' * level))
    res += self.clause.dumpParseTree(level + 1)
    res += ("\n{}]?\n".format('\t' * level))
    return res


@add_method(Rep0N)
def dumpParseTree(self, level=0):
    res = ("\n{}[\n".format('\t' * level))
    res += self.clause.dumpParseTree(level + 1)
    res += ("\n{}]*\n".format('\t' * level))
    return res


@add_method(Rep1N)
def dumpParseTree(self, level=0):
    res = ("\n{}[\n".format('\t' * level))
    res += self.clause.dumpParseTree(level + 1)
    res += ("\n{}]+\n".format('\t' * level))
    return res
