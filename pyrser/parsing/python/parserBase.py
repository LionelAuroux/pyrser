# Copyright (C) 2012 Candiotti Adrien 
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

from pyrser.parsing.python.parserStream import ParserStream

class ParserBase:
    """
    An ascii parsing primitive library.
    """
    def __init__(self, sStream = ""):
        self.__lStream = [ParserStream(sStream, "root")]
        self.__stackIgnored = [self.ignoreBlanks]
        self.__readIgnored = self.__stackIgnored[-1]
        self.ruleNodes = [{}]
        self.__ruleNode = None
        self.__rules = {}
        self.__hooks = {}

### PUBLIC ACCESSOR

    def getStream(self) -> str:
        """
        Return current used Stream.
        """
        return self.__lStream[-1]

    def printStream(self, nIndex = 0):
        """
        Print current real stream contained.
        """
        return self.getStream().printStream(nIndex)

### READ ONLY @property

    @property
    def ruleNode(self) -> object:
        """
        Return the object attach to the execution of the last rule
        """
        return self.__ruleNode

    @property
    def streamName(self) -> str:
        """
        Return current Stream name.
        """
        return self.getStream().name

    @property
    def streamLen(self) -> int:
        """
        Return the len of the current stream.
        """
        return self.getStream().contentLen

    @property
    def streamNbr(self) -> int:
        return len(self.__lStream)

    @property
    def columnNbr(self) -> int:
        """
        Return the number of column that was parsed.
        """
        return self.getStream().columnNbr

    @property
    def lineNbr(self) -> int:
        """
        Return the number of line that was parsed.
        """
        return self.getStream().lineNbr

    @property
    def index(self) -> int:
        """
        Return the index value.
        This value is used by the parser to point current byte.
        """
        return self.getStream().index

    @property
    def eofIndex(self) -> int:
        """
        Return the index of the EOF
        """
        return self.getStream().eofIndex

    @property
    def peekChar(self) -> str:
        """
        Test if head byte is equal to c and return true else return false.
        """
        return self.getStream().peekChar

### CONTEXT PRIMITIVES

    def saveContext(self) -> bool:
        """
        Stack the current index position.
        """
        self.__ruleNode = None
        return self.getStream().saveContext()

    def restoreContext(self) -> bool:
        """
        Pop the last index position and set current stream index to this value.
        """
        return self.getStream().restoreContext()

    def validContext(self) -> bool:
        """
        Pop all useless contexts to keep one context only.
        """
        return self.getStream().validContext()

### Rule Nodes

    def pushRuleNodes(self):
        """
        Push context variable to store rule nodes
        """
        self.ruleNodes.append(self.ruleNodes[-1].copy())
        pass

    def popRuleNodes(self):
        """
        Pop context variable that store rule nodes
        """
        self.ruleNodes.pop()
        pass

### STREAM

    def parsedStream(self, sNewStream : str, sName = "new"):
        """
        Push a new Stream into the parser.
        All subsequent called functions will parse this new stream,
        until the 'popStream' function is called.
        """
        self.__lStream.append(ParserStream(sNewStream, sName))

    def popStream(self):
        """
        Pop the last Stream pushed on to the parser stack.
        """
        self.__lStream.pop()


    def incPos(self) -> int:
        """
        Increment current index, column and line count.
        Should not be used, or only when sure.
        """
        return self.getStream().incPos()

### VARIABLE PRIMITIVES

# TODO: change for beginTag,endTag,getTag for multicapture, and typesetting at endTag (i.e: readCChar,readCString need transcoding)
    def beginTag(self, sName : str) -> bool:
        """
        Save the current index under the given name.
        """
        self.__readIgnored()
        return self.getStream().beginTag(sName)

    def endTag(self, sName : str) -> bool:
        """
        Extract the string between the saved index value and the current one.
        """
        return self.getStream().endTag(sName)

    def getTag(self, sName : str) -> bool:
        """
        Extract the string previously saved.
        """
        return self.getStream().getTag(sName)

    def setRules(self, rules : dict) -> bool:
        """
        Merge internal rules set with the given rules
        """
        self.__rules.update(rules)
        return True

    def setHooks(self, hooks : dict) -> bool:
        """
        Merge internal hooks set with the given hooks
        """
        self.__hooks.update(hooks)
        return True

    def evalRule(self, name : str) -> bool:
        """
        Evaluate the rule by its name
        """
        print("EVAL:" + name)
        return self.__rules[name]()

    def evalHook(self, name : str, ctx : dict) -> bool:
        """
        Evaluate the hook by its name
        """
        print("EVALHOOK: %s - %s" % (name, ctx))
        # TODO: think of hooks prototype!!!
        return self.__hooks[name](self, ctx)

### PARSING PRIMITIVES

    def peekText(self, sText) -> bool:
        """
        Same as readText but doesn't consume the stream.
        """
        nLength = len(sText)
        nSubIndex = self.index + (nLength - 1)
        if nSubIndex > self.getStream().eofIndex:
            return False
        sSubString = self.getStream().getContentAbsolute(self.getStream().index, nSubIndex)
        return sText == sSubString

    def readChar(self, cC : str) -> bool:
        """
        Consume the c head byte, increment current index and return True
        else return False. It use peekchar and it's the same as '' in BNF.
        """
        self.__readIgnored()
        if self.readEOF():
            return False
        self.saveContext()
        if self.peekChar == cC:
            self.incPos()
            return self.validContext()
        return self.restoreContext()

    def readAChar(self, cC : str) -> bool:
        """
        Consume a character if possible.
        """
        self.__readIgnored()
        if self.readEOF():
            return False
        self.saveContext()
        if self.index + 1 < self.eofIndex:
            cC = self.peekChar
            self.incPos()
            return self.validContext()
        return self.restoreContext()

    def readEOF(self) -> bool:
        """
        Returns true if reach end of the stream.
        """
        return self.index == self.eofIndex

    def readEOL(self) -> bool:
        """
        Return True if the parser can consume an EOL byte sequence.
        """
        self.__readIgnored()
        if self.readEOF():
            return False
        self.saveContext()
        self.readChar('\r')
        if self.readChar('\n'):
            return self.validContext()
        return self.restoreContext()

    def readUntil(self, cC : str, cInhibitor = '\\') -> bool:
        """
        Consume the stream while the c byte is not read, else return false
        ex : if stream is " abcdef ", readUntil("d"); consume "abcd".
        """
        self.__readIgnored()
        if self.readEOF():
            return False
        self.saveContext()
        while not self.readEOF():
            if self.peekChar == cInhibitor:
                self.incPos() # Deletion of the inhibitor.
                self.incPos() # Deletion of the inhibited character.
            if self.peekChar == cC:
                self.incPos()
                return self.validContext()
            self.incPos()
        return self.restoreContext()

    def readUntilEOF(self) -> bool:
        """
        Consume all the stream. Same as EOF in BNF
        """
        self.__readIgnored()
        if self.readEOF():
            return True
        self.saveContext()
        while self.index != self.eofIndex:
            self.incPos()
        return self.validContext()

    def readText(self, sText : str) -> bool:
        """
        Consume a strlen(text) text at current position in the stream
        else return False.
        Same as "" in BNF
        ex : readText("ls");.
        """
        self.__readIgnored()
        if self.readEOF():
            return False
        self.saveContext()
        if self.peekText(sText):
            nLength = len(sText)
            for _ in range(0, nLength):
                self.incPos
            return self.validContext()
        return self.restoreContext()

    def readInteger(self) -> bool:
        """
        Read following BNF rule else return False
        readInteger ::= ['0'..'9']+ ;
        """
        self.__readIgnored()
        if self.readEOF():
            return False
        self.saveContext()
        cC = self.peekChar
        if cC.isdigit():
                self.incPos()
                while not self.readEOF():
                    cC = self.peekChar
                    if not cC.isdigit():
                        break
                    self.incPos()
                return self.validContext()
        return self.restoreContext()

    def readIdentifier(self) -> bool:
        """
        Read following BNF rule else return False
        readIdentifier ::= ['a'..'z'|'A'..'Z'|'_']['0'..'9'|'a'..'z'|'A'..'Z'|'_']* ;
        """
        self.__readIgnored()
        if self.readEOF():
            return False
        self.saveContext()
        cC = self.peekChar
        if (cC.isalpha() or cC == '_'):
                self.incPos()
                while not self.readEOF():
                    cC = self.peekChar
                    if not (cC.isalpha() or cC.isdigit() or cC == '_'):
                        break
                    self.incPos()
                return self.validContext()
        return self.restoreContext()

    def readRange(self, begin : str, end : str) -> int:
        """
        Consume head byte if it is >= begin and <= end else return false
        Same as 'a'..'z' in BNF
        """
        self.__readIgnored()
        if self.readEOF():
            return False
        self.saveContext()
        cC = self.peekChar
        if cC >= begin and cC <= end:
            self.incPos()
            return self.validContext()
        return self.restoreContext()

    def readCString(self) -> bool:
        """
        Read following BNF rule else return False
        '"' -> ['/'| '"']
        """
        self.__readIgnored()
        self.saveContext()
        if self.readChar('\"') and self.readUntil('\"', '\\'):
            return self.validContext()
        return self.restoreContext()

    def readCChar(self) -> bool:
        # TODO: octal digit, hex digit
        """
        Read following BNF rule else return False
        "'" -> [~"/" "'"]
        """
        self.__readIgnored()
        self.saveContext()
        if self.readChar('\'') and self.readUntil('\'', '\\'):
            return self.validContext()
        return self.restoreContext()

### IGNORE CONVENTION

    def ignoreNull(self) -> bool:
        """
        Empty ignore convention for notignore
        """
        return True

    def ignoreBlanks(self) -> bool:
        """
        Consume comments and whitespace characters.
        """
        self.saveContext()
        while not self.readEOF():
            if self.peekChar not in " \t\r\n":
                return self.validContext()
            self.incPos()
        return self.validContext()

    def pushIgnore(self, ignoreConvention) -> bool:
        """
        Set the ignore convention
        """
        self.__stackIgnored.append(ignoreConvention)
        self.__readIgnored = self.__stackIgnored[-1]
        return True

    def popIgnore(self) -> bool:
        """
        Remove the last ignore convention
        """
        self.__stackIgnored.pop()
        self.__readIgnored = self.__stackIgnored[-1]
        return True

### PARSE TREE

class ParserTree:
    """
    Dummy Base class for all parse tree classes
    """

class Clauses(ParserTree):
    """
    A B C bnf primitive as a functor
    """
    def __init__(self, *clauses):
        ParserTree.__init__(self)
        self.clauses = clauses
    def __call__(self) -> bool:
        for clause in self.clauses:
            if not clause():
                return False
        return True

class Scope(ParserTree):
    """
    functor to wrap SCOPE/rule directive
    """
    # TODO: at each alt, pop/push ruleNodes
    def __init__(self, begin : Clauses, end : Clauses, clause : Clauses):
        ParserTree.__init__(self)
        self.begin = begin
        self.end = end
        self.clause = clause
    def __call__(self) -> bool:
        if self.begin() and self.clause() and self.end():
            return True
        return False

class Node(dict):
    def __str__(self):
        items = [repr(self)]
        for k, v in vars(self).items():
            items.append(".%s = %s" % (k, repr(v)))
        return ", ".join(items)

class Capture(ParserTree):
    """
    functor to handle capture variables
    """
    def __init__(self, parser : ParserBase, tagname : str, clause : Clauses):
        ParserTree.__init__(self)
        if not isinstance(parser, ParserBase):
            raise Exception("Bad Type For parser as parameter 2")
        self.tagname = tagname
        self.parser = parser
        self.clause = clause
    def __call__(self) -> bool:
        if self.parser.beginTag(self.tagname) and self.clause() and self.parser.endTag(self.tagname):
            ruleNode = self.parser.ruleNode
            if ruleNode is None: ruleNode = Node()
            text = self.parser.getTag(self.tagname)
            # TODO:try to wrap this into a better class
            ruleNode.value = text
            print("CTX CREATE %s:<%s> in\n%s" % (self.tagname, ruleNode, self.parser.ruleNodes[-1]))
            self.parser.ruleNodes[-1][self.tagname] = ruleNode
            return True
        return False

class Call(ParserTree):
    """
    functor to wrap arbitrary call in BNF clause
    """
    def __init__(self, callObject, *params):
        ParserTree.__init__(self)
        self.callObject = callObject
        self.params = params
    def __call__(self) -> bool:
        return self.callObject(*self.params)

class Alt(ParserTree):
    """
    [] | [] bnf primitive as a functor
    """
    # TODO: at each alt, pop/push ruleNodes
    def __init__(self, *clauses : Clauses):
        ParserTree.__init__(self)
        self.clauses = clauses
    def __call__(self) -> bool:
        for clause in self.clauses:
            if clause():
                return True
        return False

class RepOptional(ParserTree):
    """
    []? bnf primitive as a functor
    """
    def __init__(self, clause : Clauses):
        ParserTree.__init__(self)
        self.clause = clause
    def __call__(self) -> bool:
        self.clause()
        return True

class Rep0N(ParserTree):
    """
    []* bnf primitive as a functor
    """
    # TODO: at each turn, pop/push ruleNodes
    def __init__(self, clause : Clauses):
        ParserTree.__init__(self)
        self.clause = clause
    def __call__(self) -> bool:
        while self.clause():
            pass
        return True

class Rep1N(ParserTree):
    """
    []+ bnf primitive as a functor
    """
    # TODO: at each turn, pop/push ruleNodes
    def __init__(self, clause : Clauses):
        ParserTree.__init__(self)
        self.clause = clause
    def __call__(self) -> bool:
        if self.clause():
            while self.clause():
                pass
            return True
        return False

class Rule(ParserTree):
    """
    call a rule by his name
    """
    def __init__(self, parser : ParserBase, name : str):
        ParserTree.__init__(self)
        self.parser = parser
        self.name = name
    def __call__(self) -> bool:
        return self.parser.evalRule(self.name)

class Hook(ParserTree):
    """
    call a hook by his name
    """
    def __init__(self, parser : ParserBase, name : str):
        ParserTree.__init__(self)
        self.parser = parser
        self.name = name
    def __call__(self) -> bool:
        self.parser.evalHook(self.name, self.parser.ruleNodes[-1])
        return True
