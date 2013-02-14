from copy import copy

class ParserContext:
    def __init__(self, nIndex = 0, nCol = 1, nLine = 1):
        self.nIndex = nIndex
        self.nCol = nCol
        self.nLine = nLine
    def __str__(self):
        return "%s,%s (%s)" % (self.nLine, self.nCol, self.nIndex)

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

    def saveContext(self) -> bool:
        """
        save current parsing context
        """
        self.__lContext.append(copy(self.__context()))
        return True

    def restoreContext(self) -> bool:
        """
        rollback from previous save context
        """
        self.__lContext.pop()
        return False

    def validContext(self) -> bool:
        """
        commit parsing context modification
        """
        nCtxt = len(self.__lContext)
        self.__lContext[nCtxt - 2] = self.__context()
        self.__lContext.pop()
        return True

###

    def incPos(self) -> int:
        if self.__sString[self.__context().nIndex] == "\n":
            self.__context().nLine += 1
            self.__context().nCol = 0
        self.__context().nCol += 1
        self.__context().nIndex += 1
        return self.__context().nIndex

    def incPosOf(self, nInc):
        while nInc > 0:
            self.incPos()
            nInc -= 1

###

    @property
    def index(self) -> int:
        return self.__context().nIndex

    @property
    def peekChar(self) -> str:
        return self.__sString[self.__context().nIndex]

    @property
    def eofIndex(self) -> int:
        return self.__eofIndex

    @property
    def columnNbr(self) -> int:
        return self.__context().nCol

    @property
    def lineNbr(self) -> int:
        return self.__context().nLine

    @property
    def name(self) -> int:
        return self.__sName

    @property
    def lastRead(self) -> str:
        if self.__context().nIndex > 0:
            return self.__sString[self.__context().nIndex - 1]
        return self.__sString[0]

    @property
    def content(self) -> str:
        return self.__sString

    @property
    def contentLen(self) -> int:
        return len(self.__sString)

    def getContentAbsolute(self, begin, end) -> str:
        return self.__sString[begin:end]

    def getContentRelative(self, begin) -> str:
        return self.__sString[begin:self.__context().nIndex]

    def dumpContext(self):
        return "%s:%s\n" % (self.__sName, "\n".join(["%s" % _ for _ in self.__lContext]))

    def printStream(self, nIndex):
        for car in self.__sString[nIndex:]:
            if car.isalnum() == False:
                print('0x%x' % ord(car))
            else:
                print(car)

    def beginTag(self, sName) -> bool:
        """
        Save the current index under the given name.
        """
        self.__dTag[sName] = {'index' : self.index}
        return True

    def endTag(self, sName) -> bool:
        """
        Extract the string between the saved index value and the current one.
        """
        self.__dTag[sName]['value'] = self.getContentRelative(self.__dTag[sName]['index'])
        return True

    def getTag(self, sName) -> str:
        # TODO: search var in all context
        """
        Extract the string previously saved.
        """
        return self.__dTag[sName]['value']
