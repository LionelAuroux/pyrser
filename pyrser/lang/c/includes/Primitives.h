/*
** Copyright (C) 2012 Candiotti Adrien 
**
** This program is free software: you can redistribute it and/or modify
** it under the terms of the GNU General Public License as published by
** the Free Software Foundation, either version 3 of the License, or
** (at your option) any later version.
**
** This program is distributed in the hope that it will be useful,
** but WITHOUT ANY WARRANTY; without even the implied warranty of
** MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
**
** See the GNU General Public License for more details.
**
** You should have received a copy of the GNU General Public License
** along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#ifndef __PRIMITIVES__
#define __PRIMITIVES__

/* Primitives */

#define ReadUntil(c, inhib)	((s_cb*)__twoArg(readUntil, c, inhib))
#define ReadRange(begin, end)	((s_cb*)__twoArg(readRange, begin, end))

#define ReadChar(c) 		((s_cb*)__oneArg(readChar, c))
#define ReadText(str) 		((s_cb*)__oneArg(readText, str))

#define PeekChar(c) 		((s_cb*)__oneArg(peekChar, c))
#define PeekText(str)		((s_cb*)__oneArg(peekText, str))

#define __noArgPrimitiveDecl(fct)	__##fct = {0, (void*)&fct}
#define __noArgPrimitive(fct)		&__##fct

#define ReadWS			__noArgPrimitive(readWs)
#define ReadEOF			__noArgPrimitive(readEOF) 
#define ReadIdentifier  	__noArgPrimitive(readIdentifier)
#define ReadInteger		__noArgPrimitive(readInteger)
#define ReadUntilEOF		__noArgPrimitive(readUntilEOF)
#define ReadCString		__noArgPrimitive(readCString)
#define ReadCChar		__noArgPrimitive(readCChar)
#define NotIgnore		__noArgPrimitive(notIgnore)
#define IncPos			__noArgPrimitive(readAChar)

s_cb		__readWs;
s_cb		__readEOF;
s_cb		__readIdentifier;
s_cb		__readInteger;
s_cb		__readUntilEOF;
s_cb		__readCString;
s_cb		__readCChar;
s_cb		__notIgnore;
s_cb		__readAChar;

bool		readWs(void);
bool		readIdentifier(void);
bool		readChar(char c);
bool		readText(const char *sText);
bool		peekChar(char c);
bool		peekText(const char *sText);
bool		readUntil(char cC, char cInhibitor);
bool		readUntilEOF(void);
bool		readInteger(void);
bool		readRange(char cBegin, char cEnd);
bool		readCString(void);
bool		readCChar(void);
bool		readEOF(void);
bool		readEOFAt(int);
bool		readAChar(void);

#endif /* __PRIMITIVES__ */
