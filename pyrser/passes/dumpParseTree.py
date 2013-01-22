# simple dumpParseTree by walking tree with method add in ParseTree class

from pyrser.meta import *
from pyrser.parsing.python.parserBase import *
import inspect

@add_method(Call)
def     dumpParseTree(self, level = 0):
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
    elif self.callObject.__name__ == ParserBase.beginTag.__name__:
        return("%s[" % ('\t' * level))
    elif self.callObject.__name__ == ParserBase.endTag.__name__:
        return ("%s]:%s" % ('\t' * level, self.params[0]))
    else:
        res = "%s#call: %s" % ('\t' * level, self.callObject.__name__)
        res += "".join(["%s-param: %s" % ('\t' * (level + 1), param) for param in self.params])
        return res

@add_method(Scope)
def     dumpParseTree(self, level = 0):
    res = "\n%s[\n" % ('\t' * level)
    res += self.clause.dumpParseTree(level + 1)
    res += "\n%s]\n" % ('\t' * level)
    return res

@add_method(Clauses)
def     dumpParseTree(self, level = 0):
    return " ".join([clause.dumpParseTree(level + 1) for clause in self.clauses])

@add_method(Alt)
def     dumpParseTree(self, level = 0):
    return ("\n%s|" % ('\t' * level)).join([clause.dumpParseTree(level + 1) for clause in self.clauses])

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
