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

from pyrser.parsing.python.asciiParseStream import Stream

class AsciiParseWrapper:
    """
    An ascii parsing primitive library.
    """
    def __init__(self
            ,sStream = ""
            ,sIgnore = " \r\n\t"
            ,sCLine = "//"
            ,sCBegin = "/*"
            ,sCEnd = "*/"):
        if len(sCLine) == 0:
            raise Exception(\
                "Line comment open tag should be 1 character long at minimum")
        if len(sCBegin) < 2\
                or len(sCEnd) < 2:
                raise Exception(\
                "comment open tag and close tag should be 2 character long at minimum.")
        self.__dTag = {}
        self.__lStream = [Stream(sStream, "root", sIgnore)]
        self.__sCLine = sCLine
        # TODO: Not HERE
        self.__sCBegin = sCBegin
        self.__sCEnd = sCEnd
        self.__sIgnore = sIgnore

### PRIVATE

    def __getChar(self):
                """
                Return byte pointed by current stream index.
                """
                return self.getStream().getChar()

    def __getCharAt(self, nIndex):
                """
                Return byte pointed by the given index.
                """
                return self.getStream().getCharAt(nIndex)

    def __eofPos(self):
                """
                Return True if eof is reached.
                """
                return self.getStream().eofPos()

    def __lineComment(self):
                """
                Read a one line comment.
                """
                if self.peekText(self.__sCLine):
                        while self.readEOF() == False and self.__getChar() != '\n':
                                self.incPos()
                        return True
                return False

    def __peekTextFrom(self, sText, nIndex):
                """
                Same behaviour as peekText except that it begin at a certain index.
                """
                nLen = len(sText)
                nTextIndex = 0
                while nIndex != self.__eofPos() and nTextIndex < nLen:
                        if self.__getCharAt(nIndex) != sText[nTextIndex]:
                                return False
                        nIndex += 1
                        nTextIndex += 1
                if nTextIndex == nLen:
                        return True
                return False

    def __peekComment(self, nIndex):
                """
                Check for the end tag of a comment.
                """
                # FIXME : context save? compare perfs
                nInner = 0
                while nIndex != self.__eofPos():
                        if self.__getCharAt(nIndex) == self.__sCEnd[0]\
                                and self.__peekTextFrom(self.__sCEnd, nIndex):
                                        self.getStream().incPosOf((nIndex - self.index()) + len(self.__sCEnd))
                                        return nIndex
                        if self.__getCharAt(nIndex) == self.__sCBegin[0]\
                                and self.__peekTextFrom(self.__sCBegin, nIndex):
                                        nIndex += len(self.__sCBegin)
                                        nInner = self.__peekComment(nIndex)
                                        if nInner != 0:
                                                nIndex = nInner
                        nIndex += 1
                return 0

### PUBLIC ACCESSOR
# TODO: READ ONLY

    def getStream(self):
                """
                Return current used Stream.
                """
                return self.__lStream[-1]

    def getSteamName(self):
            """
            Return current Stream name.
            """
            return self.getStream().getName()

    def getStreamLen(self):
            """
            Return the len of the current stream.
            """
            return self.__eofPos()

    def getColumnNbr(self):
            """
            Return the number of column that was parsed.
            """
            return self.getStream().getColumnNbr()

    def getLineNbr(self):
            """
            Return the number of line that was parsed.
            """
            return self.getStream().getLineNbr()

    def printStream(self, nIndex = 0):
            """
            Print current real stream contained.
            """
            return self.getStream().printStream(nIndex)

### PARSING PRIMITIVE

    def peekChar(self, cC):
            """
            Test if head byte is equal to c and return true else return false.
            """
            return self.__getChar() == cC

    def peekText(self, sText):
        """
        Same as readText but doesn't consume the stream.
        """
        nLength = len(sText)
        nIndex = self.index()
        nTextIndex = 0
        while nIndex != self.__eofPos()\
            and nTextIndex < nLength:
                if self.__getCharAt(nIndex) != sText[nTextIndex]:
                    return False
                nIndex += 1
                nTextIndex += 1
        return nIndex == nLength

### READ PRIMITIVE

    def readChar(self, cC):
        """
        Consume the c head byte, increment current index and return True
        else return False. It use peekchar and it's the same as '' in BNF.
        """
        self.readIgnored() # TODO: in engine
        self.saveContext()
        if self.peekChar(cC):
            self.incPos()
            return self.validContext()
        return self.restoreContext()

    def readWs(self):
        """
        Consume head byte while it is contained in the WS liste.
        """
        while not self.readEOF():
            if self.__getChar() not in self.getWsList():
                #print("<%s> not in <%s>" % (bytes(self.__getChar(), "ascii"), bytes(self.getWsList(), "ascii")))
                return True
            self.incPos()
        return False

    def readAChar(self, cC):
        """
        Consume a character if possible.
        """
        self.readIgnored() # TODO: in engine
        self.saveContext()
        if self.index() + 1 < self.__eofPos():
            cC = self.__getChar()
            self.incPos()
            return self.validContext()
        return self.restoreContext()

    def readComment(self):
    #TODO: Faux
            """
            Consume all that is between and open and a close comment tag.
            """
            if self.__lineComment():
                    return True
            if self.peekText(self.__sCBegin) == False:
                    return False
            if self.__peekComment(self.index() + len(self.__sCBegin)) != 0:
                    return True
            raise Exception("No comment close tag found " + self.__sCBegin + " .")

    def readIgnored(self):
    # TODO: must be a rule forwarder
        """
        Consume comments and whitespace characters.
        """
        self.saveContext()
        self.readWs()
        return self.validContext()

    def readEOF(self):
        """
        Returns true if reach end of the stream.
        """
        return self.index() >= self.__eofPos()

    def readEOL(self):
        """
        Return True if the parser can consume an EOL byte sequence.
        """
        self.readIgnored() # TODO: in engine
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
        self.readIgnored() # TODO: in engine
        self.saveContext()
        while not self.readEOF():
            if self.peekChar(cInhibitor):
                self.incPos() # Deletion of the inhibitor.
                self.incPos() # Deletion of the inhibited character.
            if self.peekChar(cC):
                self.incPos()
                return self.validContext()
            self.incPos()
        return self.restoreContext()

    def readUntilEOF(self):
        """
        Consume all the stream. Same as EOF in BNF
        """
        self.readIgnored() # TODO: in engine
        self.saveContext()
        while self.index() != self.__eofPos():
            self.incPos()
        return self.validContext()

    def readText(self, sText):
        """
        Consume a strlen(text) text at current position in the stream
        else return False.
        Same as "" in BNF
        ex : readText("ls");.
        """
        self.readIgnored() # TODO: in engine
        self.saveContext()
        nLength = len(sText)
        nIndex = 0
        while not self.readEOF()\
            and nIndex < nLength:
                if self.__getChar() != sText[nIndex]:
                    return self.restoreContext()
                self.incPos()
                nIndex += 1
        if nIndex == nLength:
            return self.validContext()
        return self.restoreContext()

    def readInteger(self):
        """
        Read following BNF rule else return False
        readInteger ::= ['0'..'9']+ ;
        """
        self.readIgnored() # TODO: in engine
        self.saveContext()
        if self.readEOF() == False\
            and self.__getChar().isdigit():
                self.incPos()
                while not self.readEOF()\
                    and self.__getChar().isdigit():
                        self.incPos()
                return self.validContext()
        return self.restoreContext()

    def readIdentifier(self):
        """
        Read following BNF rule else return False
        readIdentifier ::= ['a'..'z'|'A'..'Z'|'_']['0'..'9'|'a'..'z'|'A'..'Z'|'_']* ;
        """
        self.readIgnored() # TODO: in engine
        self.saveContext()
        if not self.readEOF()\
            and (self.__getChar().isalpha()\
            or self.peekChar('_')):
                self.incPos()
                while not self.readEOF()\
                    and (self.__getChar().isalpha()\
                    or self.__getChar().isdigit()\
                    or self.peekChar('_')):
                        self.incPos()
                return self.validContext()
        return self.restoreContext()

    def readRange(self, begin, end):
        """
        Consume head byte if it is >= begin and <= end else return false
        Same as 'a'..'z' in BNF
        """
        self.readIgnored() # TODO: in engine
        if self.__getChar() >= begin and self.__getChar() <= end:
            self.incPos()
            return True
        return False

    def readCString(self):
        """
        Read following BNF rule else return False
        '"' -> ['/'| '"']
        """
        self.readIgnored() # TODO: in engine
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
        self.readIgnored() # TODO: in engine
        self.saveContext()
        if self.readChar('\'') and self.readUntil('\'', '\\'):
            return self.validContext()
        return self.restoreContext()

### CONTEXT

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

    def parsedStream(self, sNewStream, sName = "new", sIgnore = " \r\n\t"):
        """
        Push a new Stream into the parser.
        All subsequent called functions will parse this new stream,
        until the 'popStream' function is called.
        """
        self.__lStream.append(Stream(sNewStream, sName, sIgnore))

    def popStream(self):
        """
        Pop the last Stream pushed on to the parser stack.
        """
        self.__lStream.pop()

    def index(self):
        """
        Return the index value.
        This value is used by the parser to point current byte.
        """
        return self.getStream().index()

    def getWsList(self):
        """
        Return a string containing the ignored characters.
        """
        #return self.getStream().getWsList()
        return self.__sIgnore

    def setWsList(self, sNewWsList):
        """
        Set the list of caracter ignored by the parser.
        """
        self.getStream().setWsList(sNewWsList)

    def incPos(self):
        """
        Increment current index, column and line count.
        Should not be used, or only when sure.
        """
        return self.getStream().incPos()

# TODO: change for beginTag,endTag,getTag for multicapture, and typesetting at endTag (i.e: readCChar,readCString need transcoding)
    def setTag(self, sName):
        """
        Save the current index under the given name.
        """
        self.readIgnored() # TODO: in engine
        self.__dTag[sName] = self.index()
        return True

    def getTag(self, sName):
        """
        Extract the string between the saved index value and the current one.
        """
        return self.getStream().getContentRelative(self.__dTag[sName])

    def getStreamNbr(self):
        return len(self.__lStream)

