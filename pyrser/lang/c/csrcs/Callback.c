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
#include "Base.h"
#include "Callback.h"

bool		noArg(const s_cb* predicat)
{
  return ((bool (*)())predicat->cb)();
}

bool		oneArg(const s_cb* predicat)
{
  return ((bool (*)())predicat->cb)(((s_arg1*)predicat)->arg);
}

bool		twoArg(const s_cb* predicat)
{
  return ((bool (*)())predicat->cb)
    (((s_arg2*)predicat)->arg, ((s_arg2*)predicat)->arg2);
}

bool		threeArg(const s_cb* predicat)
{
  return ((bool (*)())predicat->cb)
    (((s_arg3*)predicat)->arg, ((s_arg3*)predicat)->arg2, ((s_arg3*)predicat)->arg3);
}

bool		(*execByArgNbr[4])(const s_cb*) =
		{&noArg, &oneArg, &twoArg, &threeArg};
