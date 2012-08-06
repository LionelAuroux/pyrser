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
#include "stream.h"
#include "Callback.h"
#include "ParsingBase.h"
#include "Primitives.h"

bool		trace(const s_cb*);

bool		allTrue(const s_cb* aPredicats[])
{
  int		index;
  int		save;

  save = getPos();
  for (index = 0; aPredicats[index] != 0x0; ++index)
    {
#ifdef TRACE
      if (trace(aPredicats[index]) == false)
#endif /* TRACE */
#ifndef TRACE
      if (execByArgNbr[aPredicats[index]->argNbr](aPredicats[index]) == false)
#endif /* TRACE*/
	{
	  setPos(save);
	  return (false);
	}
    }
  return (true);
}

bool		__zeroOrN(const s_cb* predicats[])
{
  if (allTrue(predicats) == true)
    {
      while (allTrue(predicats) == true)
	/*pass*/;
    }
  return (true);
}

bool		__oneOrN(const s_cb* predicats[])
{
  if (allTrue(predicats) == true)
    {
      while (allTrue(predicats) == true)
	/*pass*/;
    }
  return (false);
}

bool		__zeroOrOne(const s_cb* predicats[])
{
  allTrue(predicats);
  return (true);
}

bool		__not(const s_cb* predicats[])
{
  return (allTrue(predicats) == false);
}

bool		__complement(const s_cb* predicats[])
{
  if (allTrue(predicats))
    {
      incPos();
      return (true);
    }
  return (false);
}

bool		__alt(const s_cb* predicats[])
{
  int		index;
  int		save;

  for (index = 0; predicats[index] != 0x0; ++index)
    {
      save = getPos();
      if (execByArgNbr[predicats[index]->argNbr](predicats[index]) == true)
	return (true);
      setPos(save);
    }
  return (false);
}

bool		__until(const s_cb* predicats[])
{
  int		nSave;

  nSave = getPos();
  while (allTrue(predicats) == false)
    {
      incPos();
      if (readEOF() == true)
	{
	  setPos(nSave);
	  return (false);
	}
    }
  return (true);
}
