# simple dumpParseTree by walking tree with method add in ParseTree class

from pyrser.meta import *
from pyrser.parsing.python.parserBase import *
import inspect

@add_method(Call)
def     dumpParseTree(self, level = 0):
 #   print("%s[" % ('\t' * level))
    if self.callObject.__name__ == ParserBase.readRange.__name__:
        print("%s'%s'..'%s'" % ('\t' * level, self.params[0], self.params[1]))
    elif self.callObject.__name__ == ParserBase.readChar.__name__:
        print("%s'%s'" % ('\t' * level, self.params[0]))
    elif self.callObject.__name__ == ParserBase.readText.__name__:
        print("%s\"%s\"" % ('\t' * level, self.params[0]))
    elif self.callObject.__name__ == ParserBase.readInteger.__name__:
        print("%s#num" % ('\t' * level))
    elif self.callObject.__name__ == ParserBase.readIdentifier.__name__:
        print("%s#id" % ('\t' * level))
    elif self.callObject.__name__ == ParserBase.beginTag.__name__:
        print("%s[" % ('\t' * level))
        return
    elif self.callObject.__name__ == ParserBase.endTag.__name__:
        print("%s]:%s" % ('\t' * level, self.params[0]))
    else:
        print("%s#call: %s" % ('\t' * level, self.callObject.__name__))
        for param in self.params:
            print("%s-param: %s" % ('\t' * (level + 1), param))
 #   print("%s]" % ('\t' * level))

@add_method(Clauses)
def     dumpParseTree(self, level = 0):
    for clause in self.clauses:
        clause.dumpParseTree(level + 1)


@add_method(Alt)
def     dumpParseTree(self, level = 0):
    for clause in self.clauses:
        print("%s|" % ('\t' * level))
        clause.dumpParseTree(level + 1)

@add_method(RepOptional)
def     dumpParseTree(self, level = 0):
    print("%s[" % ('\t' * level))
    self.clause.dumpParseTree(level + 1)
    print("%s]?" % ('\t' * level))

@add_method(Rep0N)
def     dumpParseTree(self, level = 0):
    print("%s[" % ('\t' * level))
    self.clause.dumpParseTree(level + 1)
    print("%s]*" % ('\t' * level))

@add_method(Rep1N)
def     dumpParseTree(self, level = 0):
    print("%s[" % ('\t' * level))
    self.clause.dumpParseTree(level + 1)
    print("%s]+" % ('\t' * level))
