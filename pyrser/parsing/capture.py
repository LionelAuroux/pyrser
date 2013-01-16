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


def capture(oPredicat, sName, dDict, bConsumeWs=True):
    """
    Capture the bytes consumed by a predicat.
    """
    if bConsumeWs:
        Parsing.oBaseParser.readIgnored()
    Parsing.oBaseParser.setTag(sName)
    bRes = oPredicat()
    if bRes:
        if ((sName in dDict) == False
                or not isinstance(dDict[sName], type({}))):
            dDict[sName] = Parsing.oBaseParser.getTag(sName)
    return bRes


class Capture(object):
    """
    Capture function functor.
    """
    def __init__(self, oPredicat, sName, dDict, bConsumeWs=True):
        self.__oPredicat = oPredicat
        self.__sName = sName
        self.__dDict = dDict
        self.__bConsumeWs = bConsumeWs

    def __call__(self):
        return\
            capture(self.__oPredicat, self.__sName,
                    self.__dDict, self.__bConsumeWs)
