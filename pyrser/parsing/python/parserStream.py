from copy import copy

class ParserContext:
    def __init__(self, nIndex = 0, nCol = 1, nLine = 1):
        self.nIndex = nIndex
        self.nCol = nCol
        self.nLine = nLine

class ParserStream:
    def __init__(self, sString = "", sName = "stream"):
        self.__sString = sString
        self.__eofIndex = len(sString)
        self.__sName = sName
        self.__lContext = [ParserContext()]
        self.__dTag = {}

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

###

    def incPos(self):
        if self.peekChar == "\n":
            self.__context().nLine += 1
            self.__context().nCol = 0
        self.__context().nCol += 1
        self.__context().nIndex += 1

    def incPosOf(self, nInc):
        while nInc > 0:
            self.incPos()
            nInc -= 1

###

    @property
    def index(self):
        return self.__context().nIndex

    @property
    def peekChar(self):
        return self.__sString[self.__context().nIndex]

    @property
    def eofIndex(self):
        return self.__eofIndex

    @property
    def columnNbr(self):
        return self.__context().nCol

    @property
    def lineNbr(self):
        return self.__context().nLine

    @property
    def name(self):
        return self.__sName

    @property
    def lastRead(self):
        if self.__context().nIndex > 0:
            return self.__sString[self.__context().nIndex - 1]
        return self.__sString[0]

    @property
    def content(self):
        return self.__sString

    @property
    def contentLen(self):
        return len(self.__sString)

#    def peekCharAt(self, nIndex):
#        return self.__sString[nIndex]

    def getContentAbsolute(self, begin, end):
        return self.__sString[begin:end]

    def getContentRelative(self, begin):
        return self.__sString[begin:self.__context().nIndex]

    def printStream(self, nIndex):
        for car in self.__sString[nIndex:]:
            if car.isalnum() == False:
                print('0x%x' % ord(car))
            else:
                print(car)

    def beginTag(self, sName):
        """
        Save the current index under the given name.
        """
        self.__dTag[sName] = {'index' : self.index}
        return True

    def endTag(self, sName):
        """
        Extract the string between the saved index value and the current one.
        """
        self.__dTag[sName]['value'] = self.getContentRelative(self.__dTag[sName]['index'])
        return True

    def getTag(self, sName):
        """
        Extract the string previously saved.
        """
        return self.__dTag[sName]['value']
