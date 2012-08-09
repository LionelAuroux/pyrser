from asciiParseStream import Stream

class AsciiParseWrapper:
      """
      An ascii parsing primitive library.
      """
      def __init__(self
		   ,sStream = ""
		   ,sIgnore = " \r\n\t"
		   ,sCLine = "//"
		   ,sCEnd = "*/"):

          if len(sCLine) == 0:
            raise Exception(\
	  "Line comment open tag should be 1 character long at minimum")

          if len(sCBegin) < 2\
           or len(sCEnd) < 2:
	     raise Exception(\
	  "comment open tag and close tag should be 2 character long at minimum.")

##### private:
	  self.__dTag = {}
	  self.__lStream = [Stream(sStream, "first", sIgnore)]

      def __stream(self):
	  """
	  Return current used Stream.
	  """
          return self.__lStream[-1]

      def __getChar(self):
	  """
	  Return byte pointed by current stream index.
	  """
          return self.__stream().getChar()

      def __eofPos(self):
	  """
	  Return True if eof is reached.
	  """
          return self.__stream().eofPos()

##### public:
      def readComment(self):
	  """
	  """
          pass

      def readWs(self):
          """
	  Consume head byte while it is contained in the WS liste.
	  """
	  while self.readEOF() == False:
	    if self.__getChar() in self.getWsList():
	      return True
	    self.incPos()
	  return True 

      def readIgnored(self):
          """
	  docstring for readIgnored
	  """
          pass

      def peekChar(self, cC):
          """
	  Test if head byte is equal to c and return true else return false.
	  """
          return self.__getChar() == cC

      def readChar(self, cC):
          """
	  Consume the c head byte, increment current index and return True
	  else return False. It use peekchar and it's the same as '' in BNF.
	  """
          self.readWs()
	  if peekChar(cC) == True:
	    self.incPos()
	    return True
	  return False

      def peekText(self, sText):
          """
	  Same as readText but doesn't consume the stream.
	  """
	  nIndex = 0
          nLength = len(sText)
	  self.saveContext()
	  while self.readEOF() == False\
	    and nIndex < nLength:
	    if self.__getChar() != sText[nIndex]
	      self.restoreContext()
	      return False
	    self.incPos()
	    nIndex += 1
	  self.restoreContext()
	  return nIndex == nLength

      def lastRead(self):
          """
	  Return last Consumed byte
	  """
          return self.__stream().lastRead()

      def readEOF(self):
          """
	  Returns true if reach end of the stream.
	  """
          return self.getIndex() == self.__eofPos()

      def readEOL(self):
	  """
	  Return True if the parser can consume an EOL byte sequence.
	  """
          self.readChar('\r')
	  if self.readChar('\n'):
	    return self.validContext()
	  self.restoreContext()
	  return False

      def readUntil(self, cC, cInhibitor):
          """
	  Consume the stream while the c byte is not read, else return false
	  ex : if stream is " abcdef ", readUntil("d"); consume "abcd".
	  """
          self.saveContext()
	  while self.readEOF() == False:
	    if self.peekChar(cInhibitor) == True:
	      self.incPos()
	    if self.readChar(cC) == True:
	      return self.validContext()
	  self.restoreContext()
	  return False

      def readUntilEOF(self):
          """
	  Consume all the stream. Same as EOF in BNF
	  """
	  while self.getIndex() != self.__eofPos():
	    self.incPos()
	  return True

      def readText(self, sText):
          """
	  Consume a strlen(text) text at current position in the stream
	  else return False.
	  Same as "" in BNF
	  ex : readText("ls");.
	  """
	  nIndex = 0
          nLength = len(sText)
	  self.saveContext()
	  while self.readEOF() == False\
	    and nIndex < nLength:
	    if self.__getChar() != sText[nIndex]
	      self.restoreContext()
	      return False
	    self.incPos()
	    nIndex += 1
	  if nIndex == nLength:
	    return self.validContext()
	  self.restoreContext()
	  return False

      def readInteger(self):
          """
	  Read following BNF rule else return False
	  readInteger ::= ['0'..'9']+ ;
	  """
          self.readWs()
	  if self.readEOF() == False\
	    and self.__getChar().isdigit():
	    self.incPos()
	    while self.readEOF() == False\
	      and self.__getChar().isdigit():
		self.incPos()
	    return True
	  return False

      def readIdentifier(self):
	  """
	  Read following BNF rule else return False
	  readIdentifier ::= ['a'..'z'|'A'..'Z'|'_']['0'..'9'|'a'..'z'|'A'..'Z'|'_']* ;
	  """
          self.readWs()
	  if self.readEOF() == False\
	    and self.__getChar().isalpha()\
	    or self.__getChar() == '_':
	    self.incPos()
	    while self.readEOF() == False\
	      and (self.__getChar().isalpha()\
		or self.__getChar().isdigit()\
		or self.__getChar() == '_')
	      self.incPos()
	    return True
	  return False
      
      def readRange(self, begin, end):
          """
	  Consume head byte if it is >= begin and <= end else return false
	  Same as 'a'..'z' in BNF
	  """
          self.readWs()
	  if self.__getChar() >= begin\
	    and self.__getChar() <= end:
	    self.incPos()
	    return True
	  return False

	def readCString(self):
            """
	    Read following BNF rule else return False
	    '"' -> ['/'| '"']
	    """
	    self.saveContext()
	    if self.readChar('\"') == True\
	      and self.readUntil('\"', '\\') == True:
	      return self.validContext()
	    self.restoreContext()
	    return False

	def readCChar(self):
            """
	    Read following BNF rule else return False
	    "'" -> ["/"| "'"]
	    """
	    self.saveContext()
	    if self.readChar('\'') == True\
	      and self.readUntil('\'', '\\') == True:
	      return self.validContext()
	    self.restoreContext()
	    return False

	def saveContext(self):
            """
	    Stack the current index position.
	    """
	    self.__stream().saveContext()

	def restoreContext(self):
            """
	    Pop the last index position and set current stream index to this value.
	    """
	    self.__stream().restoreContext()

	def validContext(self):
            """
	    Pop all useless contexts to keep one context only.
	    """
	    self.__stream().validContext()

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

	def setWsList(self, sNewWsList):
	    """
	    Set the list of caracter ignored by the parser.
	    """
	    self.__stream().setWsList(sNewWsList)

	def getIndex(self):
            """
	    Return the index value.
	    This value is used by the parser to point current byte.
	    """
	    return self.__stream.getIndex()

	def getColumnNbr(self):
            """
	    Return the number of column that was parsed.
	    """
	    return self.__stream.getColumnNbr()

	def getLineNbr(self):
            """
	    Return the number of line that was parsed.
	    """
	    return self.__stream.getLineNbr()

	def getStreamLen(self):
	    """
	    Return the len of the current stream.
	    """
	    return self.__eofPos()

	def getCurrentByte(self):
            """
	    Return the current pointed byte.
	    """
	    return self.__getChar()

	def getWsList(self):
	    """
	    Return a string containing the ignored characters.
	    """
	    return self.__stream().getWsList()

	def getName(self):
	    """
	    Return current Stream name.
	    """
	    return self.__stream().getName()

	def getStream(self):
	    """
	    Return the current analysed Stream.
	    """
	    return self.__stream().getStream()

	def printStream(self):
	    """
	    Print current real stream contained in the wrapped c++.
	    """
	    return self.__stream().printStream()

	def incPos(self):
            """
	    Increment current index, column and line count.
	    Should not be used, or only when sure.
	    """
	    return self.__stream().incPos()
