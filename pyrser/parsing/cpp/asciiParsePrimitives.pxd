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

cdef extern from *:
    ctypedef char* ccptr "const char*" 

cdef extern from "asciiParsePrimitives.h":
  cdef cppclass AsciiParse:
        AsciiParse(char*, char*, char*, char*, char*)

        void		readWs()
        bint		readComment()
        void		readIgnored()
        char		lastRead()
        bint		peekChar(char)
        bint		readChar(char)
        bint		readEOF()
        bint		readEOL()
        bint		readUntil(char, char)
        bint		readUntilEOF()
        bint		peekText(char*)
        bint		readText(char*)
        bint		readInteger()
        bint		readIdentifier()
        bint		readRange(char, char)
        bint		readCString()
        bint		readCChar()
        bint		readAChar()
        void		saveContext()
        bint		restoreContext()
        bint		validContext()
        void		parsedStream(char*, char*, char*)
        void		popStream()
        void		setWsList(char*)
        char*		getWsList()
        int		getIndex()
        int		getColumnNbr()
        int		getLineNbr()
        int		getStreamLen()
        char		getCurrentByte()
        char*		getName()
        void		printStream()
        void		incPos()
        ccptr		getStream()

cdef extern from "Python.h":
  object PyString_FromStringAndSize(char *s, Py_ssize_t len)

