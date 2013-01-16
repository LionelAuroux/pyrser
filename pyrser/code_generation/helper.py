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


class CodeGenerationHelper(object):
    """
    The code generation helper class.
    """
    def __init__(self, dConf):
        self.__nDepth = 1
        self.__lCount = [self.Count(0, 0)]
        self.__lAlt = [False]
        self.__lAltCount = [self.Count(0, 0)]
        self.__dGlobals = {}
        self.__dConf = dConf

    class Count(object):
        def __init__(self, nCount, nLength):
            self.nCount = nCount
            self.nLength = nLength

    def builtin(self, sName):
        return self.__dConf['builtins'][sName]

    def keyword(self, sName):
        return self.__dConf['keyword'][sName]

    def multiplier(self, sName):
        return self.__dConf['multiplier'][sName]

    def not_(self, sName):
        return self.__dConf['not'][sName]

    def accessOperator(self):
        return self.__dConf['accessOperator']

    def alt(self):
        return self.__dConf['alt']

    def baseParserAccess(self):
        return self.__dConf['baseParserMethod']\
            + self.__dConf['accessOperator']

    def baseParser(self):
        return self.__dConf['keyword']['object']\
            + self.__dConf['accessOperator']\
            + self.__dConf['baseParserMethod']

    def accessInstance(self):
        return self.__dConf['keyword']['object']\
            + self.__dConf['accessOperator']

    def upPrimitives(self):
        return self.__dConf['upPrimitives']

    def capitalize(self, sString):
        return '%s%s' % (sString[0].capitalize(), sString[1:])

    def pushCount(self, nCount, nLength):
        self.__lCount.append(self.Count(nCount, nLength))
        return ""

    def popCount(self):
        self.__lCount.pop()
        return ""

    def incCount(self):
        self.__lCount[-1].nCount += 1
        return ""

    def incDepth(self):
        self.__nDepth += 1
        return ""

    def decDepth(self):
        self.__nDepth -= 1
        return ""

    def pushAlt(self, bAlt, nAltLength=0):
        self.__lAlt.append(bAlt)
        self.__lAltCount.append(self.Count(0, nAltLength))
        return ""

    def popAlt(self):
        self.__lAlt.pop()
        self.__lAltCount.pop()
        return ""

    def altCount(self):
        return self.__lAltCount[-1].nCount

    def altLength(self):
        return self.__lAltCount[-1].nLength

    def incAltCount(self):
        self.__lAltCount[-1].nCount += 1
        return ""

    def count(self):
        return self.__lCount[-1].nCount

    def length(self):
        return self.__lCount[-1].nLength

    def inAlt(self):
        return self.__lAlt[-1] == True

    def inDepth(self):
        return self.__nDepth > 1

    def inRecurse(self):
        return self.inDepth() or self.inAlt()

    def getattr(self, oObject, sName):
        return oObject._TemplateReference__context[sName]

    def indent(self):
        return ' ' * self.__dConf['indent'] * self.__nDepth

    def setGlobal(self, sName, oValue):
        self.__dGlobals[sName] = oValue
        return ""

    def getGlobal(self, sName):
        return self.__dGlobals[sName]
