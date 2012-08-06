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
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include "Base.h"
#include "stream.h"
#include "Lifo.h"

static lifo	__lStream = {NULL, 0};

void		pushStream(char* string)
{
  s_stream*	oNew;

  if ((oNew = malloc(sizeof(*oNew))) == NULL)
    {
      printf("Error : malloc failed.\n");
      exit(-1);
    }
  oNew->string = string;
  oNew->index = 0;
  oNew->length = strlen(string);
  push(&__lStream, oNew);
}

void		popStream(void)
{
  s_stream*	pRm;

  if ((pRm = top(&__lStream)) != NULL)
    {
      pop(&__lStream);
      free(pRm);
    }
}

void		setPos(int newIndex)
{
  s_stream*	pCurrent;

  if ((pCurrent = top(&__lStream)) != NULL)
    pCurrent->index = newIndex;
}

int		getPos(void)
{
  s_stream*	pCurrent;

  if ((pCurrent = top(&__lStream)) != NULL)
    return(pCurrent->index);
  return (-1);
}

void		incPos(void)
{
  setPos(getPos() + 1);
}

char		getByte(int index)
{
  s_stream*	pCurrent;

  if ((pCurrent = top(&__lStream)) != NULL)
    return pCurrent->string[index];
  return (-1);
}

char		getCurrentByte(void)
{
  s_stream*	pCurrent;

  if ((pCurrent = top(&__lStream)) != NULL)
    return pCurrent->string[pCurrent->index];
  return (-1);
}

bool		atEOF()
{
  s_stream*	pCurrent;

  if ((pCurrent = top(&__lStream)) != NULL)
    return (pCurrent->index >= pCurrent->length);
  return (true);
}

char*		__substr(int nStart, int nEnd)
{
  s_stream*	pCurrent;
  char*		sStr;
  int		nSize;

  nSize = nEnd - nStart;
  if ((sStr = malloc(sizeof(*sStr) * nSize)) == NULL)
    {
      printf("Error : malloc failed.\n");
    }
  if ((pCurrent = top(&__lStream)) != NULL)
    return (strncpy(sStr, &pCurrent->string[nStart], nSize));
  return NULL;
}
