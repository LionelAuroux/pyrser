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

from pyrser.parsing.parsing_context import parsingContext
from pyrser.parsing.dont_consume import dontConsume

from pyrser.parsing import Parsing


class SlotExpressionFunctor(type):
    def __new__(oCls, sName, lBases, dDct):
        """
        A metaclass to slot the bnf primitive functors.
        """
        dDct['__slots__'] = {'__lPredicats': None}
        return type.__new__(oCls, sName, lBases, dDct)


def allTrue(*lPredicats):
    """
    Check if iEach predicats is True
    """
    for iEach in lPredicats:
        if iEach() == False:
            return False
    return True


@parsingContext
def zeroOrOne(*lPredicats):
    """
    []? bnf primitive
    """
    allTrue(*lPredicats)
    return True


@parsingContext
def zeroOrN(*lPredicats):
    """
    []* bnf primitive
    """
    if allTrue(*lPredicats):
        while allTrue(*lPredicats):
            pass
    return True


@parsingContext
def oneOrN(*lPredicats):
    """
    []+ bnf primitive
    """
    if allTrue(*lPredicats):
        while allTrue(*lPredicats):
            pass
        return True
    return False


def alt(*lPredicats):
    """
    [] | [] bnf primitive
    """
    for iEach in lPredicats:
        if iEach():
            return True
    return False


@parsingContext
def expression(*lPredicats):
    """
    [] bnf primitive
    """
    return allTrue(*lPredicats)


@parsingContext
def until(*lPredicats):
    """
    ->[] bnf primitive
    """
    while allTrue(*lPredicats) == False:
        Parsing.oBaseParser.incPos()
        if Parsing.oBaseParser.readEOF():
            return False
    return True


@dontConsume
def negation(*lPredicats):
    """
    ![] bnf primitive
    """
    if allTrue(*lPredicats):
        return False
    return True


@parsingContext
def complement(*lPredicats):
    """
    ~[] bnf primitive
    """
    if allTrue(*lPredicats):
        return False
    Parsing.oBaseParser.incPos()
    return True


@dontConsume
def lookAhead(*lPredicats):
    """
    =[] bnf primitive
    """
    return allTrue(*lPredicats)

# FIXME : context pb?


@parsingContext
def n(oPredicat, nFrom, nTo=None):
    """
    {} bnf primitive
    """
    if nTo == None:
        nTo = nFrom

    nCount = 0
    nIndex = 0

    while nIndex < nTo:
        if oPredicat() == True:
            nCount += 1
        nIndex += 1

    if nTo == None:
        return nCount == nFrom
    return nCount >= nFrom and nCount <= nTo

##### functors:


class ZeroOrOne:
    """
    []? bnf primitive as a functor
    """
    __metaclass__ = SlotExpressionFunctor

    def __init__(self, *lPredicats):
        self.__lPredicats = lPredicats

    def __call__(self):
        return zeroOrOne(*self.__lPredicats)


class ZeroOrN:
    """
    []* bnf primitive as a functor
    """
    __metaclass__ = SlotExpressionFunctor

    def __init__(self, *lPredicats):
        self.__lPredicats = lPredicats

    def __call__(self):
        return zeroOrN(*self.__lPredicats)


class OneOrN:
    """
    []+ bnf primitive as a functor
    """
    __metaclass__ = SlotExpressionFunctor

    def __init__(self, *lPredicats):
        self.__lPredicats = lPredicats

    def __call__(self):
        return oneOrN(*self.__lPredicats)


class Expression:
    """
    [] bnf primitive as a functor
    """
    __metaclass__ = SlotExpressionFunctor

    def __init__(self, *lPredicats):
        self.__lPredicats = lPredicats

    def __call__(self):
        return expression(*self.__lPredicats)


class Alt:
    """
    [] | [] bnf primitive as a functor
    """
    __metaclass__ = SlotExpressionFunctor

    def __init__(self, *lPredicats):
        self.__lPredicats = lPredicats

    def __call__(self):
        return alt(*self.__lPredicats)


class Until:
    """
    ->[] bnf primitive as a functor
    """
    __metaclass__ = SlotExpressionFunctor

    def __init__(self, *lPredicats):
        self.__lPredicats = lPredicats

    def __call__(self):
        return until(*self.__lPredicats)


class Negation:
    """
    ![] bnf primitive as a functor
    """
    __metaclass__ = SlotExpressionFunctor

    def __init__(self, *lPredicats):
        self.__lPredicats = lPredicats

    def __call__(self):
        return negation(*self.__lPredicats)


class Complement:
    """
    ~[] bnf primitive as a functor
    """
    __metaclass__ = SlotExpressionFunctor

    def __init__(self, *lPredicats):
        self.__lPredicats = lPredicats

    def __call__(self):
        return complement(*self.__lPredicats)


class LookAhead(object):
    """
    =[] bnf primitive as a functor
    """
    __metaclass__ = SlotExpressionFunctor

    def __init__(self, *lPredicats):
        self.__lPredicats = lPredicats

    def __call__(self):
        return lookAhead(*self.__lPredicats)


class N:
    """
    {} bnf primitive as a functor
    """
    def __init__(self, oPredicat, nFrom, nTo=None):
        self.__oPredicat = oPredicat
        self.__nFrom = nFrom
        self.__nTo = nTo

    def __call__(self):
        return n(self.__oPredicat, self.__nFrom, self.__nTo)
