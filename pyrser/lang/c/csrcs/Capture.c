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
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include "Base.h"
#include "CallBack.h"
#include "Lifo.h"
#include "Capture.h"
#include "stream.h"
#include "ParsingBase.h"
#include "Primitives.h"

bool		__capture(const s_cb* predicats[], char* name, lifo* lCpt)
{
  int		nTmp;
  char*		sCaptured;

  nTmp = getPos();
  readWs();
  if (allTrue(predicats) == true)
    {
      sCaptured = __substr(nTmp, getPos());
      addCapture(lCpt, name, sCaptured);
      return (true);
    }
  return (false);
}

void		addCapture(lifo* lList, char* sName, char* sCaptured)
{
  s_capturePair* oNewPair;

  if ((oNewPair = malloc(sizeof(*oNewPair))) == NULL)
    {
      printf("Error : malloc failed.\n");
      exit(-1);
    }
  oNewPair->name = sName;
  oNewPair->captured = sCaptured;
  push(lList, oNewPair);
}

void		cleanCapture(lifo* lList)
{
  s_node*	pNodeToRm;

  while ((lList->stack) != NULL)
    {
      free((lList->stack)->data);
      pNodeToRm = lList->stack;
      lList->stack = (lList->stack)->next;
      free(pNodeToRm);
    }
}

char*		getCapture(lifo* lList, char* sName)
{
  s_node	*lStack;

  lStack = lList->stack;
  for (;lStack != NULL; lStack = lStack->next)
    {
      if (!strcmp(inPair(lStack)->name, sName))
	return (inPair(lStack)->captured);
    }
  return (NULL);
}
