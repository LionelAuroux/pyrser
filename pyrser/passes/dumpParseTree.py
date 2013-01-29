# simple dumpParseTree by walking tree with method add in ParseTree class
# 
# This pass is for debug only

from pyrser.meta import *
from pyrser.parsing.python.parserBase import *
import inspect

@add_method(Call)
def     dumpParseTree(self, level = 0):
    # TODO: Think of remaping of method to hook
    if self.callObject.__name__ == ParserBase.readRange.__name__:
        return ("%s'%s'..'%s'" % ('\t' * level, self.params[0], self.params[1]))
    elif self.callObject.__name__ == ParserBase.readChar.__name__:
        return ("%s'%s'" % ('\t' * level, self.params[0]))
    elif self.callObject.__name__ == ParserBase.readText.__name__:
        return ("%s\"%s\"" % ('\t' * level, self.params[0]))
    elif self.callObject.__name__ == ParserBase.readInteger.__name__:
        return ("%s#num" % ('\t' * level))
    elif self.callObject.__name__ == ParserBase.readIdentifier.__name__:
        return ("%s#id" % ('\t' * level))
    else:
        res = "%s#call: %s (" % ('\t' * level, self.callObject.__name__)
        res += ", ".join(["%s" % repr(param) for param in self.params])
        res += ")"
        return res

@add_method(Scope)
def     dumpParseTree(self, level = 0):
    res = "\n%s[%s\n" % ('\t' * (level + 1), self.begin.dumpParseTree(0))
    res += self.clause.dumpParseTree(level + 1)
    res += "\n%s]%s\n" % ('\t' * (level + 1), self.end.dumpParseTree(0))
    return res

@add_method(Capture)
def     dumpParseTree(self, level = 0):
    res = "\n%s[\n" % ('\t' * level)
    res += self.scope.clause.dumpParseTree(level + 1)
    res += "\n%s] : %s\n" % ('\t' * level, self.tagname)
    return res

@add_method(Clauses)
def     dumpParseTree(self, level = 0):
    return " ".join([clause.dumpParseTree(level + 1) for clause in self.clauses])

@add_method(Alt)
def     dumpParseTree(self, level = 0):
    res = "\n%s  %s" % ('\t' * level, self.clauses[0].dumpParseTree(0))
    res += ("\n%s| " % ('\t' * level)).join([clause.dumpParseTree(0) for clause in self.clauses[1:]])
    return res

@add_method(RepOptional)
def     dumpParseTree(self, level = 0):
    res = ("\n%s[\n" % ('\t' * level))
    res += self.clause.dumpParseTree(level + 1)
    res += ("\n%s]?\n" % ('\t' * level))
    return res

@add_method(Rep0N)
def     dumpParseTree(self, level = 0):
    res = ("\n%s[\n" % ('\t' * level))
    res += self.clause.dumpParseTree(level + 1)
    res += ("\n%s]*\n" % ('\t' * level))
    return res

@add_method(Rep1N)
def     dumpParseTree(self, level = 0):
    res = ("\n%s[\n" % ('\t' * level))
    res += self.clause.dumpParseTree(level + 1)
    res += ("\n%s]+\n" % ('\t' * level))
    return res
