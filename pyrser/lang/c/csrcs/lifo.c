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
#include <stdio.h>
#include "Lifo.h"

void		push(lifo* lList, void* oData)
{
  s_node*	oNew;

  if ((oNew = malloc(sizeof(*oNew))) == NULL)
    {
      printf("Error : malloc failed\n");
      exit(-1);
    }
  oNew->data = oData;
  oNew->next = lList->stack;
  lList->stack = oNew;
  lList->size = lList->size + 1;
}

void		pop(lifo* lList)
{
  s_node*	pRm;

  pRm = lList->stack;
  if (lList->stack != NULL)
    {
      lList->stack = (lList->stack)->next;
      lList->size = lList->size - 1;
      free(pRm);
    }
}

void*		top(lifo* lList)
{
  if (lList->stack != NULL)
    return ((lList->stack)->data);
  return (NULL);
}

size_t		size(lifo* lList)
{
  return (lList->size);
}
