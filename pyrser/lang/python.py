# Copyright (C) 2012 Candiotti Adrien
# Copyright (C) 2013 Pascal Bertrand
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

python = {
    'builtins': {
        'identifier': 'readIdentifier',
        'num': 'readInteger',
        'string': 'readCString',
        'cchar': 'readCChar',
        'char': 'readAChar',
        'space': 'readWs',
        'end': 'readUntilEOF',
        'empty': 'readEOF',
        'super': 'super',
        'false': 'false',
        'readThisChar': 'readChar',
        'readThisText': 'readText',
        'range': 'readRange',
        'notIgnore': 'notIgnore',
        'resetIgnore': 'resetIgnore',
        },
    'not': {
        '!': 'negation',
        '~': 'complement',
        },
    'multiplier': {
        '?': 'zeroOrOne',
        '+': 'oneOrN',
        '*': 'zeroOrN',
        '[]': 'expression',
        '{}': 'n'
        },
    'keyword': {'and': 'and', 'object': 'self'},
        'accessOperator': '.',
        'alt': 'alt',
        'baseParserMethod': 'Parsing.oBaseParser',
        'indent': 15,
        'file_extension': '.py',
        }

from imp import load_source


def pythonPostGeneration(sModuleName, sFile, sToFile, sGrammar, oInstance):
    oModule = load_source(sModuleName, sToFile)
    if sGrammar != None:
        try:
            oClass = getattr(oModule, sGrammar)
            return oClass
        except:
            oInstance.error("""No grammar called "%s" in %s""" % (sGrammar, sFile))
            exit(0)
    return oModule
