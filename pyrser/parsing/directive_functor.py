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

from pyrser.parsing import Parsing


class ReadText(object):
    """
    Encapsulation of the 'readText' primitive into a functor.
    """
    __slots__ = {'__name__': 'ReadText', '__sText': None}

    def __init__(self, sText):
        self.__sText = sText

    def __call__(self):
        return Parsing.oBaseParser.readText(self.__sText)


class ReadChar(object):
    """
    Encapsulation of the 'readChar' primitive into a functor.
    """
    __slots__ = {'__name__': 'ReadChar', '__cChar': None}

    def __init__(self, cChar):
        self.__cChar = cChar

    def __call__(self):
        return Parsing.oBaseParser.readChar(self.__cChar)


class ReadUntil(object):
    """
    Encapsulation of the 'readUntil' primitive into a functor.
    """
    __slots__ = {'__name__': 'ReadUntil', '__cChar': None}

    def __init__(self, cChar):
        self.__cChar = cChar

    def __call__(self):
        return Parsing.oBaseParser.readUntil(self.__cChar)


class ReadRange:
    """
    Encapsulation of the 'readRange' primitive into a functor.
    """
    __slots__ = {'__name__': 'ReadRange',
                 '__cBegin': None,
                 '__cEnd': None}

    def __init__(self, cBegin, cEnd):
        self.__cBegin = cBegin
        self.__cEnd = cEnd

    def __call__(self):
        return Parsing.oBaseParser.readRange(self.__cBegin, self.__cEnd)


class NonTerminal:
    """
    Encapsulate nonTerminal rule execution into a functor.
    """
    __slots__ = ('__oPredicat', '__oNode')

    def __init__(self, oPredicat, oNode):
        self.__oPredicat = oPredicat
        self.__oNode = oNode

    def __call__(self):
        return self.__oPredicat(self.__oNode)


class Hook:
    """
    Encapsulate hook execution into a functor.
    """
    __slots__ = ('__oPredicat', '__oNode')

    def __init__(self, oPredicat, oNode, *lArgs):
        self.__oPredicat = oPredicat
        self.__oNode = oNode
        self.__lArgs = lArgs

    def __call__(self):
        return self.__oPredicat(self.__oNode, *self.__lArgs)


class Super:
    """
    Encapsulate super() function into a functor.
    """
    __slots__ = ('__oParentClass', '__oTarget', '__sRuleName', '__oNode')

    def __init__(self, oParentClass, oTarget, sRuleName, oNode):
        self.__oParentClass = oParentClass
        self.__oTarget = oTarget
        self.__sRuleName = sRuleName
        self.__oNode = oNode

    def __call__(self):
        return getattr(self.__oParentClass, self.__sRuleName)\
            (self.__oTarget, self.__oNode)


class NotIgnore:
    """
    Encapsulate notIgnore directive into a functor.
    """
    __slots__ = ()

    def __call__(self):
        return Parsing.oBaseParser.notIgnore()


class FalseDirective:
    """
    Return false to ease debug.
    """
    __slots__ = ()

    def __call__(self):
        return Parsing.oBaseParser.false()


class ResetIgnore(object):
    """
    Encapsulate ResetIgnore directive into a functor.
    """
    __slots__ = ()

    def __init__(self):
        return Parsing.oBaseParser.resetIgnore()
