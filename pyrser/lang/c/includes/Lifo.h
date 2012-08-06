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

#ifndef __LIFO__
#define __LIFO__

typedef struct	t_node
{
  void*		data;
  struct t_node*next;
}		s_node;

typedef struct	t_lifo
{
  s_node*	stack;
  size_t	size;
}		lifo;

void		push(lifo*, void*);
void		pop(lifo*);
void*		top(lifo*);
size_t		size(lifo*);

#endif /* __LIFO__ */
