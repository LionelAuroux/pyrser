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
#include <ctype.h>
#include <string.h>
#include "Base.h"
#include "stream.h"
#include "Callback.h"
#include "Primitives.h"

bool		readEOF()
{
  return atEOF();
}

bool		readEOFAt(int nIndex)
{
  return (getByte(nIndex) == '\0');
}

bool		readWs(void)
{
  int		tmp = getPos();

  while (readEOFAt(tmp) == false
      && (strchr(WSLIST, getByte(tmp))))
    tmp = tmp + 1;
  setPos(tmp);
  return (true);
}

bool		readChar(char c)
{
  readWs();
  if (getCurrentByte() == c)
    {
      incPos();
      return (true);
    }
  return (false);
}

bool		peekChar(char c)
{
  readWs();
  return (getCurrentByte() == c);
}

bool		peekText(const char *sText)
{
  int		nIndex;
  int		nTmp;

  readWs();
  nTmp = getPos();
  nIndex = 0;
  while (sText[nIndex] != '\0')
    {
      if (getByte(nTmp) != sText[nIndex])
	return (false);
      nTmp = nTmp + 1;
      nIndex = nIndex + 1;
    }
  return true;
}

bool		readText(const char *sText)
{
  int		nIndex;
  int		nTmp;

  readWs();
  nTmp = getPos();
  nIndex = 0;
  while (sText[nIndex] != '\0')
    {
      if (getByte(nTmp) != sText[nIndex])
	return (false);
      nTmp = nTmp + 1;
      nIndex = nIndex + 1;
    }
  setPos(nTmp);
  return (true);
}

bool		readUntil(char cC, char cInhibitor)
{
  int		nSave;

  readWs();
  nSave = getPos();
  while (readEOF() == false)
    {
      readChar(cInhibitor);
      if (readChar(cC) == true)
	return (true);
      incPos();
    }
  setPos(nSave);
  return (false);
}

bool		readUntilEOF(void)
{
  int		nTmp;

  readWs();
  nTmp = getPos();
  while (readEOFAt(nTmp) == false)
    nTmp = nTmp + 1;
  setPos(nTmp);
  return (true);
}

bool		readInteger(void)
{
  int		nTmp;

  readWs();
  nTmp = getPos();
  if (readEOFAt(nTmp) == false && isdigit(getByte(nTmp)))
    {
      nTmp = nTmp + 1;
      while (readEOFAt(nTmp) == false && isdigit(getByte(nTmp)))
	nTmp = nTmp + 1;
      setPos(nTmp);
      return (true);
    }
  return (false);
}

bool		readRange(char cBegin, char cEnd)
{
  int		nTmp;

  readWs();
  nTmp = getPos();
  if (getByte(nTmp) >= cBegin && getByte(nTmp) <= cEnd)
    {
      setPos(nTmp + 1);
      return (true);
    }
  return (false);
}

bool		readCString(void)
{
  int		nTmp;

  readWs();
  nTmp = getPos();
  if (readChar('"') && readUntil('"', '\\'))
    return (true);
  return (false);
}

bool		readCChar(void)
{
  int		nTmp;

  readWs();
  nTmp = getPos();
  if (readChar('\'') && readUntil('\'', '\\'))
    return (true);
  return (false);
}

bool		readIdentifier(void)
{
  int		tmp;

  readWs();
  tmp = getPos();
  if (isalpha(getByte(tmp)) || getByte(tmp) == '_')
    {
      tmp = tmp + 1;
      while (readEOFAt(tmp) == false
	  && (isalpha(getByte(tmp))
	    || getByte(tmp) == '_'
	    || isdigit(getByte(tmp))))
	tmp = tmp + 1;
      setPos(tmp);
      return (true);
    }
  return (false);
}

bool		notIgnore(void)
{
  return (true);
}

bool		readAChar(void)
{
  readWs();
  incPos();
  return (true);
}

s_cb		__noArgPrimitiveDecl(readWs);
s_cb		__noArgPrimitiveDecl(readEOF);
s_cb		__noArgPrimitiveDecl(readIdentifier);
s_cb		__noArgPrimitiveDecl(readInteger);
s_cb		__noArgPrimitiveDecl(readUntilEOF);
s_cb		__noArgPrimitiveDecl(readCString);
s_cb		__noArgPrimitiveDecl(readCChar);
s_cb		__noArgPrimitiveDecl(notIgnore);
s_cb		__noArgPrimitiveDecl(readAChar);
