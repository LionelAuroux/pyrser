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
#include <stdio.h>
#include "Base.h"
#include "Callback.h"
#include "ParsingBase.h"
#include "Primitives.h"
#include "trace.h"

const char*	resstr[] = {"false", "true"};

typedef struct  t_debug
{
  void*		addr;
  const char*	name;
}		s_debug;

s_debug		debugDictionnary[]=
{
  {__zeroOrN, "zeroOrN"},
  {__zeroOrOne, "zeroOrOne"},
  {__oneOrN, "oneOrN"},
  {allTrue, "expression"},
  {__not, "not"},
  {readIdentifier, "#identifier"},
  {readChar, "#char"},
  {readText, "readText"}
}
;

bool		trace(const s_cb* oPredicat)
{
  int		index;
  bool		bRes;

  bRes = execByArgNbr[oPredicat->argNbr](oPredicat);
  for (index = 0;
      index < (int)(sizeof(debugDictionnary)/sizeof(debugDictionnary[0]));
      ++index)
    {
      if (debugDictionnary[index].addr == oPredicat->cb)
	{
	  printf("%s : %s\n", debugDictionnary[index].name, resstr[bRes]);
	  return (bRes);
	}
    }
  return( bRes);
}
