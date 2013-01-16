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

from parsing import Parsing

dWsList = {"base": " \t\r\n"}


def addWsList(sName, sWsList):
    dWsList[sName] = sWsList


class ignore(object):
    """
    A decorator that specify the wsList
    """
    def __init__(self, sWsList):
        if sWsList.upper() in dWsList:
            self.__sWsList = dWsList[sWsList.upper()]
        else:
            self.__sWsList = sWsList

    def __call__(self, oRule):
        def wrapper(*lArgs):
            sOldWsList = Parsing.oBaseParser.getWsList()
            Parsing.oBaseParser.setWsList(self.__sWsList)
            bRes = oRule(*lArgs)
            Parsing.oBaseParser.setWsList(sOldWsList)
            return bRes
        return wrapper
