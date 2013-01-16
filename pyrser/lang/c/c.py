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

c =\
    {
        'builtins':
        {'identifier': 'readIdentifier', 'num': 'readInteger', 'string': 'readCString', 'cchar': 'readCChar', 'char': 'readAChar', 'space': 'readWs', 'end': 'readUntilEOF', 'empty': 'readEOF', 'super': 'super', 'notIgnore': 'notIgnore', 'false': 'false', 'readThisChar': 'readChar', 'readThisText': 'readText'},

        'not': {'!': 'negation', '~': 'complementary'},

        'multiplier': {'?': 'zeroOrOne', '+': 'oneOrN', '*': 'zeroOrN', '[]': 'expression'},

        'keyword': {'and': '&&', 'object': ''},
        'accessOperator': '',
        'alt': 'alt',
        'baseParserMethod': '',
        'upPrimitives': 'False',
        'indent': 6,
        'file_extension': '.c'
    }

from imp import load_source


def cPostGeneration(sModuleName, sFile, sToFile, sGrammar, oInstance):
    print 'c file generation over'
    # FIXME : add compilation of example
    # generate a main function and call start rule in it
    # compile with gcc -I lib/lang/c/includes -L lib/lang/clib
    exit(0)
