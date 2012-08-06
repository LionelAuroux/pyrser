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
#include "Lifo.h"
#include "Context.h"

static lifo __lContextList = {NULL, 0};

void			saveContext(void)
{
  s_parsingContext	*oNew;
  s_parsingContext	*oOld;

  if ((oNew = malloc(sizeof(*oNew))) == NULL)
    {
      printf("Error : malloc failed.");
      exit(-1);
    }
  if ((oOld = top(&__lContextList)) != NULL)
    oNew = memcpy(oOld, oNew, sizeof(*oOld));
  else
    {
      oNew->index = 0;
      oNew->wslist = WSLIST;
    }
  push(&__lContextList, oNew);
}

bool			restoreContext(void)
{
  s_parsingContext	*toRm;

  toRm = top(&__lContextList);
  pop(&__lContextList);
  free(toRm);
  return (false);
}

bool			validContext(void)
{
  int			nSize;
  s_parsingContext*	pLast;
  s_parsingContext*	pToRm;

  nSize = size(&__lContextList);
  if (nSize < 2)
    {
      printf("Context error : %d context, should be 2.\n", nSize);
      exit(-1);
    }
  pLast = top(&__lContextList);
  pop(&__lContextList);
  pToRm = top(&__lContextList);
  pop(&__lContextList);
  push(&__lContextList, pLast);
  free(pToRm);
  return (true);
}

void			setWsList(char* sWsList)
{
  s_parsingContext*	pLast;

  if ((pLast = top(&__lContextList)) != NULL)
    pLast->wslist = sWsList;
}
