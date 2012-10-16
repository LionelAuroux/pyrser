from asciiParseContext import AsciiParseContext
from copy import copy

class Stream:
      def __init__(self, sString = "", sName = "stream", sIgnore = " \r\n\t"):

##### private:
	  self.__neofPos = len(sString)
	  self.__sString = sString
	  self.__sName = sName
	  self.__lContext = [AsciiParseContext()]

      def __context(self):
          return self.__lContext[-1]

##### public:

      def saveContext(self):
          self.__lContext.append(copy(self.__context()))

      def restoreContext(self):
          self.__lContext.pop()

      def validContext(self):
          nCtxt = len(self.__lContext)
#	  if nCtxt < 2:
#	    error("Context error. (Context nbr == 1)", self)
	  self.__lContext[nCtxt - 2] = self.__context()
	  self.__lContext.pop()
#	  if len(self.__lContext) == 0:
#	    error("Context error. (No context)", self)

      def setWsList(self, sWsList):
          self.__context().sWsList = sWsList

      def getWsList(self):
          return self.__context().sWsList

      def index(self):
          return self.__context().nIndex

      def incPos(self):
	  if self.getChar() == "\n":
	    self.__context().nLine += 1
	    self.__context().nCol = 0
	  self.__context().nCol += 1
	  self.__context().nIndex += 1

      def incPosOf(self, nInc):
	  while nInc > 0:
	    self.incPos()
	    nInc -= 1

      def getChar(self):
          return self.__sString[self.__context().nIndex]

      def getCharAt(self, nIndex):
          return self.__sString[nIndex]

      def eofPos(self):
          return self.__neofPos

      def getColumnNbr(self):
          return self.__context().nCol

      def getLineNbr(self):
          return self.__context().nLine

      def getName(self):
          return self.__sName

      def lastRead(self):
	  if self.__context().nIndex > 0:
	    return self.__sString[self.__context().nIndex - 1]
	  return self.__sString[0]

      def getStream(self):
	  return self.__sString

      def printStream(self, nIndex):
	  while nIndex < self.__neofPos:
	    if self.getCharAt(nIndex).isalnum() == False:
	      print '0x%x' % ord(self.getCharAt(nIndex)),
	    else:
	      print self.getCharAt(nIndex),
	    nIndex += 1
	  print
