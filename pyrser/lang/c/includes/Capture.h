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

#ifndef __CAPTURE__
#define __CAPTURE__

#define Capture(name, cpt, ...) ((const s_cb*)\
				__threeArg(__capture, ARRAY(__VA_ARGS__), name, cpt))
#define capture(name, cpt, ...) __capture(ARRAY(__VA_ARGS__), name, cpt)
#define inPair(list)		(((s_capturePair*)list->data))
#define node(parent)		{parent, {NULL, 0}}

typedef	struct	t_capturePair
{
  char*		name;
  char*		captured;
}		s_capturePair;

typedef	struct	t_ctx
{
  struct t_ctx*	parent;
  lifo		localCapture;
}		s_ctx;

bool		__capture(const s_cb*[], char*, lifo*);
void		addCapture(lifo*, char*, char*);
void		cleanCapture(lifo*);
char*		getCapture(lifo*, char*);

#endif /* __CAPTURE__ */
