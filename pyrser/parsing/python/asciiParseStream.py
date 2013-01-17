from copy import copy


class AsciiParseContext:
    def __init__(self, nIndex = 0, nCol = 1, nLine = 1, sWsList = " \r\n\t"):
        self.nIndex = nIndex
        self.nCol = nCol
        self.nLine = nLine
        self.sWsList = sWsList

class Stream:
    def __init__(self, sString = "", sName = "stream", sIgnore = " \r\n\t"):
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
        return False

    def validContext(self):
        nCtxt = len(self.__lContext)
        self.__lContext[nCtxt - 2] = self.__context()
        self.__lContext.pop()
        return True

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

    def getContent(self):
        return self.__sString

    def getContentAbsolute(self, begin, end):
        return self.__sString[begin:end]

    def getContentRelative(self, begin):
        return self.__sString[begin:self.__context().nIndex]

    def printStream(self, nIndex):
        while nIndex < self.__neofPos:
            if self.getCharAt(nIndex).isalnum() == False:
                print('0x%x' % ord(self.getCharAt(nIndex)))
            else:
                print(self.getCharAt(nIndex))
        nIndex += 1
