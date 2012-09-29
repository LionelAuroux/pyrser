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

from asciiParsePrimitives cimport AsciiParse, PyString_FromStringAndSize, ccptr

cdef class AsciiParseWrapper:
      """
      A parsing primitive library.
      """
      cdef AsciiParse* __oParser
      cdef object      __dTag
      cdef object      __lStream
      cdef object      __oRoot

      def __init__(self\
		   ,char* stream = ""\
		   ,char* ignore = " \r\n\t"\
		   ,char* sCLine = "//"\
		   ,char* sCBegin = "/*"\
		   ,char* sCEnd = "*/"):
          """ Python initialisation. """

          if len(sCLine) == 0:
            print\
      'Error : line comment open tag should be 1 character long at minimum'

          if len(sCBegin) < 2\
           or len(sCEnd) < 2:
             print\
      'Error : comment open tag and close tag should be 2 character long at minimum.'
             exit(1)

##### private:
          cdef str sStr = stream
          self.__oParser = new AsciiParse(stream, ignore, sCLine, sCBegin, sCEnd)
          self.__dTag = {}
          self.__lStream = [sStr]
          self.__oRoot = None

##### public:

      def __dealloc__(self):
          """ .Dtor """
          del self.__oParser

      def root(self):
          return self.__oRoot

      def setRoot(self, oRoot):
          self.__oRoot = oRoot

      def readComment(self):
          """
	  Consume all that is between and open and a close comment tag.
	  """
          self.__oParser.readComment()

      def readIgnored(self):
          """
	  Consume comments and whitespace characters.
	  """
          self.__oParser.readIgnored()

      def readWs(self):
          """
	  Consume head byte while it is contained in the WS liste.
	  """
          self.__oParser.readWs()
          return True

      def lastRead(self):
          """
	  Return last Consumed byte
	  """
          return self.__oParser.lastRead()

      cpdef bint	peekChar(self, c):
            """
	    Test if head byte is equal to c and return true else return false.
	    """
            if (len(c) != 1):
              raise TypeError
            return self.__oParser.peekChar(ord(c))

      cpdef bint readChar(self, c):
            """
	    Consume the c head byte, increment current index and return True
	    else return False. It use peekchar and it's the same as '' in BNF.
	    """
            if (len(c) != 1):
              raise TypeError('readChar argument len was greater than one.')
            return self.__oParser.readChar(ord(c))

      cpdef bint readEOF(self):
            """
	    Returns true if reach end of the stream.
	    """
            return self.__oParser.readEOF()

      cpdef bint readUntil(self, c, delimitor = '\\'):
            """
	    Consume the stream while the c byte is not read, else return false
	    ex : if stream is " abcdef ", readUntil("d"); consume "abcd".
	    """
            if (len(c) != 1 or len(delimitor) != 1):
              raise TypeError
            return self.__oParser.readUntil(ord(c), ord(delimitor))
 
      cpdef bint readUntilEOF(self):
            """
	    Consume all the stream. Same as EOF in BNF
	    """
            return self.__oParser.readUntilEOF()

      cpdef bint peekText(self, char* text):
            """
	    Same as readText but doesn't consume the stream.
	    """
            return self.__oParser.peekText(text)

      cpdef bint readText(self, char* text):
            """
	    Consume a strlen(text) text at current position in the stream
	    else return False.
	    Same as "" in BNF
	    ex : readText("ls");.
	    """
            return self.__oParser.readText(text)

      cpdef bint readInteger(self):
            """
	    Read following BNF rule else return False
	    readInteger ::= ['0'..'9']+ ;
	    """
            return self.__oParser.readInteger()

      cpdef bint readIdentifier(self):
            """
	    Read following BNF rule else return False
	    readIdentifier ::= ['a'..'z'|'A'..'Z'|'_']['0'..'9'|'a'..'z'|'A'..'Z'|'_']* ;
	    """
            return self.__oParser.readIdentifier() 

      cpdef bint readRange(self, begin, end):
            """
	    Consume head byte if it is >= begin and <= end else return false
	    Same as 'a'..'z' in BNF
	    """
            return self.__oParser.readRange(ord(begin), ord(end))

      cpdef bint readCString(self):
            """
	    Read following BNF rule else return False
	    '"' -> ['/'| '"']
	    """
            return self.__oParser.readCString()

      cpdef bint readCChar(self):
            """
	    Read following BNF rule else return False
	    "'" -> ["/"| "'"]
	    """
            return self.__oParser.readCChar()

      cpdef bint  readAChar(self):
            """
	    Consume a character if possible.
	    """
            return self.__oParser.readAChar()

      def   incPos(self):
            """
	    Increment current index, column and line count.
	    Should not be used, or only when sure.
	    """
            self.__oParser.incPos()

      def   notIgnore(self):
            """
	    Stop ignoring characters from wsList.
	    """
            self.setWsList("")
            return True

      def   resetIgnore(self):
            """
	    Reset ignored characters list.
	    """
            self.setWsList(" \r\n\t")
            return True

      def   saveContext(self):
            """
	    Stack the current index position.
	    """
            self.__oParser.saveContext()

      def   restoreContext(self):
            """
	    Pop the last index position.
	    """
            return self.__oParser.restoreContext()

      def   validContext(self):
            """
	    Pop all useless contexts to keep one context only.
	    """
            return self.__oParser.validContext()

      def   parsedStream(self, char* newStream,\
			       char* name = "<string>",\
			       char* ignore = " \r\n\t"):
            """
	    Push a new Stream into the parser.
	    All subsequent called functions will parse this new stream,
	    until the 'popStream' function is called.
	    """
            self.__lStream.append(newStream)
            self.__oParser.parsedStream(newStream, name, ignore)

      def  popStream(self):
           """
	   Pop the last Stream pushed on to the parser stack.
	   """
           self.__lStream.pop()
           self.__oParser.popStream()

      def  getStream(self):
           """
	   Return the current analysed Stream.
	   """
           return self.__lStream[-1]

      def  getStreamLen(self):
           """
	   Return the len of the current stream.
	   """
           return self.__oParser.getStreamLen()

      def  printStream(self):
           """
	   Print current real stream contained in the wrapped c++.
	   """
           self.__oParser.printStream()

      def  setWsList(self, char* newWsList):
           """
	   Set the list of caracter ignored by the parser.
	   """
           self.__oParser.setWsList(newWsList)
      
      def  getWsList(self):
           """
	   Return the list of characters ignored by the parser
	   """
           return self.__oParser.getWsList()

      cpdef int getColumnNbr(self):
            """
	    Return the number of column that was parsed.
	    """
            return self.__oParser.getColumnNbr()

      cpdef int getLineNbr(self):
            """
	    Return the number of line that was parsed.
	    """
            return self.__oParser.getLineNbr()

      cpdef int getIndex(self):
            """
	    Return the index value.
	    This value is used by the parser to point current byte.
	    """
            return self.__oParser.getIndex()

      cpdef char getCurrentByte(self):
            """
	    Return the current pointed byte.
	    """
            return self.__oParser.getCurrentByte()

      cpdef getName(self):
            """
	    Return the name gived to the current Stream.
	    """
            return self.__oParser.getName()

      cpdef setTag(self, char* tagName):
            """
	    Save the current index under the given name.
	    """
            self.__dTag[tagName] = self.getIndex()
            return True

      cpdef object	getTag(self, char* tagName):
            """
	    Extract the string between the saved index value
	    and the current one.
	    """
            cdef int origin = self.__dTag[tagName]
            cdef ccptr stream = &(self.__oParser.getStream()[origin])
            if self.getIndex() <= origin:
              return PyString_FromStringAndSize("", 0)
            return PyString_FromStringAndSize(stream, self.getIndex() - origin)

      cpdef object	getCTag(self, char* tagName):
            """
	    Same as getTag but it suppress the last caracter:
	    usefull in the cas of a C String or Char.
	    """
            cdef int origin = self.__dTag[tagName]
            cdef ccptr stream = &(self.__oParser.getStream()[origin])
            return PyString_FromStringAndSize(stream,\
		(self.getIndex() - origin) - 1)
