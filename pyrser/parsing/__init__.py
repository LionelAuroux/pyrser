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

from pyrser.parsing.python.AsciiParseWrapper import AsciiParseWrapper


class Parsing(object):
    oParserClass = AsciiParseWrapper
    oBaseParser = oParserClass('')
#      oFinalParser = oBaseParser


def getParserClass():
    return Parsing.oParserClass


def setBaseParser(oBaseParser):
    Parsing.oBaseParser = oBaseParser


def resetBaseParser(sStream="", sIgnore=" \r\n\t", sCLine="//", sCBegin="/*", sCEnd="*/"):
    setBaseParser(getParserClass()(sStream, sIgnore, sCLine, sCBegin, sCEnd))
