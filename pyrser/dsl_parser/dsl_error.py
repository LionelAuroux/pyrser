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


class GrammarException(Exception):
    def __init__(self, sText):
        super(Exception, self).__init__('In %s line %d column %d : %s'
                                        % (Parsing.oBaseParser.getName(),
                                           Parsing.oBaseParser.getLineNbr(),
                                           Parsing.oBaseParser.getColumnNbr(),
                                           sText))


class Error:
    """
    Local GrammarException encapsulation into a functor.
    """
    def __init__(self, sMsg):
        self.__sMsg = sMsg

    def __call__(self):
        raise GrammarException(self.__sMsg)
