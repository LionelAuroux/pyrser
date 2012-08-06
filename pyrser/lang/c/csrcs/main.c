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
#include <string.h>
#include <stdlib.h>
#include "Base.h"
#include "Lifo.h"
#include "Callback.h"
#include "ParsingBase.h"
#include "Primitives.h"
#include "stream.h"
#include "Context.h"
#include "Capture.h"


/*--------------------------------*/
/* rule test code*/
/* __{$className}__{$ruleName}Rule*/

/*--------------------------------*/
bool		__expression__expressionRule(s_ctx* oParentCtx);

int main(int argc, char *argv[])
{
  extern const char*	resstr[];
  bool	res;

  if (argc == 2)
    {
      pushStream(argv[1]);
      saveContext();
      s_ctx		oLocalCtx = {{NULL, 0}, NULL};
      /*res = rule(csv, csv);*/
      /*res = rule(ini, ini, &oLocalCtx) && readEOF();*/
//      res = rule(debug, debug, &oLocalCtx);
      printf("%d\n", getPos());
      /*res = rule(lisp, s_expression, &oLocalCtx);*/
      /*double i = 1;
      while (i < 10000000)
	{
      */
      res = rule(expression, expression, &oLocalCtx);
	  /*i = i + 1;
	}*/
      printf("[%s]\n", resstr[getPos() == (int)strlen(argv[1])]);

      /*
      popStream();
      pushStream(argv[2]);
      res = rule(debug, debug);
      printf("[%s]\n", resstr[getPos() == (int)strlen(argv[2])]);
      */
    }
  return 0;
}
