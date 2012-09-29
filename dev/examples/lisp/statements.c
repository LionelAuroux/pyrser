#include <stdio.h>
#include "lisp.h"
#include "statements.h"

const atom*		__condition(const atom** list)
{
  if (list[0] != 0 && list[1] != 0)
    {
      if (final_value(list[0]) == true)
	{
	  final_value(list[1]);
	  return (atom_res(BOOLEAN, true));
	}
      else if (list[2] != 0)
	{
	  final_value(list[2]);
	  return (atom_res(BOOLEAN, true));
	}
    }
  return (atom_res(BOOLEAN, false));
}

const atom*		__print(const atom** list)
{
  int			index;

  for (index = 0; list[index] != 0; ++index)
    {
      if (type(list[index]) == STRING)
	printf("%s", string_value(list[index]));
      else
	printf("%ld", final_value(list[index]));
    }
  printf("\n");
  return (atom_res(BOOLEAN, true));
}
