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

#ifndef __CALLBACK__
#define __CALLBACK__

/* Helpers */
#define	ARRAY(...) 		((const s_cb*[]){__VA_ARGS__, 0x0})

#define __threeArg(fct, arg, arg2, arg3)\
		  &(s_arg3){{3, (void*)&fct}, (void*)arg, (void*)arg2, (void*)arg3}
#define __twoArg(fct, arg, arg2)&(s_arg2){{2, (void*)&fct}, (void*)arg, (void*)arg2}
#define __oneArg(fct, arg)	&(s_arg1){{1, (void*)&fct}, (void*)arg}
#define __noArg(fct) 		&(s_cb){0, (void*)&fct}

typedef	struct	t_cb
{
  int		argNbr;
  void		*cb;
}		s_cb;

typedef	struct	t_Arg1
{
 s_cb		base;
 void*		arg;
}		s_arg1;

typedef	struct	t_Arg2
{
 s_cb		base;
 void*		arg;
 void*		arg2;
}		s_arg2;

typedef	struct	t_Arg3
{
 s_cb		base;
 void*		arg;
 void*		arg2;
 void*		arg3;
}		s_arg3;

extern bool	(*execByArgNbr[4])(const s_cb*);

bool		noArg(const s_cb* predicat);
bool		oneArg(const s_cb* predicat);
bool		twoArg(const s_cb* predicat);
bool		threeArg(const s_cb* predicat);

#endif /* __CALLBACK__ */
