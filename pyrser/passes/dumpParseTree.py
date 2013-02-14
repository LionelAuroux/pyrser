# Copyright (C) 2013 Lionel Auroux
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# simple dumpParseTree by walking tree with method add in ParseTree class

# This pass is for debug only

from pyrser.meta import *
from pyrser.parsing.python.parserBase import *
import inspect

@add_method(ParserBase)
def dumpParseTree(self):
    res = "{"
    for k,v in self.rules.items():
        if isinstance(v, ParserTree):
            res += "\n\t%s : %s" % (repr(k), v.dumpParseTree(1))
            res += "\t,"
        else:
            res += "\n\t%s : %s," % (repr(k), repr(v))
    res += "\n}"
    return res

@add_method(Rule)
def     dumpParseTree(self, level = 0):
    return "%s%s" % ('\t' * level, self.name)

@add_method(Hook)
def     dumpParseTree(self, level = 0):
    return "%s#%s" % ('\t' * level, self.name)

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
    res += self.clause.dumpParseTree(level + 1)
    res += "\n%s] : %s\n" % ('\t' * level, self.tagname)
    return res

@add_method(Clauses)
def     dumpParseTree(self, level = 0):
    return " ".join([clause.dumpParseTree(level + 1) for clause in self.clauses])

@add_method(Alt)
def     dumpParseTree(self, level = 0):
    res = "\n%s  %s" % ('\t' * level, self.clauses[0].dumpParseTree(0))
    if len(self.clauses) > 1: res += "\n%s| " % ('\t' * level)
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
