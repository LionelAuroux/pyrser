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
from functools import wraps


def dontConsume(oTarget):
    @wraps(oTarget)
    def wrapper(*lArgs):
        Parsing.oBaseParser.saveContext()
        bRes = oTarget(*lArgs)
        Parsing.oBaseParser.restoreContext()
        return bRes
    return wrapper
