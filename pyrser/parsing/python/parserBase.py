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
        self.__readIgnored = self.ignoreBlanks

### PUBLIC ACCESSOR

    def getStream(self):
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
    def streamName(self):
        """
        Return current Stream name.
        """
        return self.getStream().name

    @property
    def streamLen(self):
        """
        Return the len of the current stream.
        """
        return self.getStream().contentLen

    @property
    def streamNbr(self):
        return len(self.__lStream)

    @property
    def columnNbr(self):
        """
        Return the number of column that was parsed.
        """
        return self.getStream().columnNbr

    @property
    def lineNbr(self):
        """
        Return the number of line that was parsed.
        """
        return self.getStream().lineNbr

    @property
    def index(self):
        """
        Return the index value.
        This value is used by the parser to point current byte.
        """
        return self.getStream().index

    @property
    def eofIndex(self):
        """
        Return the index of the EOF
        """
        return self.getStream().eofIndex

    @property
    def peekChar(self):
        """
        Test if head byte is equal to c and return true else return false.
        """
        return self.getStream().peekChar

### CONTEXT PRIMITIVES

    def saveContext(self):
        """
        Stack the current index position.
        """
        return self.getStream().saveContext()

    def restoreContext(self):
        """
        Pop the last index position and set current stream index to this value.
        """
        return self.getStream().restoreContext()

    def validContext(self):
        """
        Pop all useless contexts to keep one context only.
        """
        return self.getStream().validContext()

### STREAM

    def parsedStream(self, sNewStream, sName = "new"):
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


    def incPos(self):
        """
        Increment current index, column and line count.
        Should not be used, or only when sure.
        """
        return self.getStream().incPos()

### VARIABLE PRIMITIVES

# TODO: change for beginTag,endTag,getTag for multicapture, and typesetting at endTag (i.e: readCChar,readCString need transcoding)
    def beginTag(self, sName):
        """
        Save the current index under the given name.
        """
        self.__readIgnored()
        return self.getStream().beginTag(sName)

    def endTag(self, sName):
        """
        Extract the string between the saved index value and the current one.
        """
        return self.getStream().endTag(sName)

    def getTag(self, sName):
        """
        Extract the string previously saved.
        """
        return self.getStream().getTag(sName)

### PARSING PRIMITIVES

    def peekText(self, sText):
        """
        Same as readText but doesn't consume the stream.
        """
        nLength = len(sText)
        nSubIndex = self.index + (nLength - 1)
        if nSubIndex > self.getStream().eofIndex:
            return False
        sSubString = self.getStream().getContentAbsolute(self.getStream().index, nSubIndex)
        return sText == sSubString

    def readChar(self, cC):
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

    def readAChar(self, cC):
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

    def readEOF(self):
        """
        Returns true if reach end of the stream.
        """
        return self.index == self.eofIndex

    def readEOL(self):
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

    def readUntil(self, cC, cInhibitor = '\\'):
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

    def readUntilEOF(self):
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

    def readText(self, sText):
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

    def readInteger(self):
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

    def readIdentifier(self):
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

    def readRange(self, begin, end):
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

    def readCString(self):
        """
        Read following BNF rule else return False
        '"' -> ['/'| '"']
        """
        self.__readIgnored()
        self.saveContext()
        if self.readChar('\"') and self.readUntil('\"', '\\'):
            return self.validContext()
        return self.restoreContext()

    def readCChar(self):
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

    def ignoreNull(self):
        """
        Empty ignore convention for notignore
        """
        return True

    def ignoreBlanks(self):
        """
        Consume comments and whitespace characters.
        """
        self.saveContext()
        while not self.readEOF():
            if self.peekChar not in " \t\r\n":
                return self.validContext()
            self.incPos()
        return self.validContext()

    def setIgnore(self, func):
        """
        Set the ignore convention
        """
        self.__readIgnored = func
        return True

### PARSE TREE

class ParserTree:
    """
    Dummy Base class for all parse tree classes
    """
    pass

class Scope(ParserTree):
    """
    functor to wrap SCOPE/rule directive
    """
    def __init__(self):
        pass

class Call(ParserTree):
    """
    functor to wrap arbitrary call in BNF clause
    """
    def __init__(self, callObject, *params):
        self.callObject = callObject
        self.params = params
    def __call__(self):
        return self.callObject(*self.params)

class Clauses(ParserTree):
    """
    [] bnf primitive as a functor
    """
    def __init__(self, *clauses):
        self.clauses = clauses
    def __call__(self):
        for clause in self.clauses:
            if not clause():
                return False
        return True

class Alt(ParserTree):
    """
    [] | [] bnf primitive as a functor
    """
    def __init__(self, *clauses):
        self.clauses = clauses
    def __call__(self):
        for clause in self.clauses:
            if clause():
                return True
        return False

class RepOptional(ParserTree):
    """
    []? bnf primitive as a functor
    """
    def __init__(self, clause):
        self.clause = clause
    def __call__(self):
        self.clause()
        return True

class Rep0N(ParserTree):
    """
    []* bnf primitive as a functor
    """
    def __init__(self, clause):
        self.clause = clause
    def __call__(self):
        while self.clause():
            pass
        return True

class Rep1N(ParserTree):
    """
    []+ bnf primitive as a functor
    """
    def __init__(self, clause):
        self.clause = clause
    def __call__(self):
        if self.clause():
            while self.clause():
                pass
            return True
        return False

