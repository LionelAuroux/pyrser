#include <stdio.h>
#include <stdlib.h>
#include "lisp.h"

const atom*	__add(const atom** list)
{
  int		index;
  long int	res;

  res = 0;
  for (index = 0; list[index] != 0; ++index)
    res += final_value(list[index]);
  return (atom_res(INTEGER, res));
}

const atom*		__minus(const atom** list)
{
  int		index;
  long int	res;

  res = 0;
  if (list[0] != 0)
    {
      res = final_value(list[0]);
      for (index = 1; list[index] != 0; ++index)
	res -= final_value(list[index]);
    }
  return (atom_res(INTEGER, res));
}

const atom*		__time(const atom** list)
{
  int		index;
  long int	res;

  res = 0;
  if (list[0] != 0)
    {
      res = final_value(list[0]);
      for (index = 1; list[index] != 0; ++index)
	res *= final_value(list[index]);
    }
  return (atom_res(INTEGER, res));
}

const atom*		__divide(const atom** list)
{
  int		index;
  long int	res;

  res = 0;
  if (list[0] != 0)
    {
      res = final_value(list[0]);
      for (index = 1; list[index] != 0; ++index)
	res /= final_value(list[index]);
    }
  return (atom_res(INTEGER, res));
}

const atom*		__modulus(const atom** list)
{
  int		index;
  long int	res;

  res = 0;
  for (index = 0; list[index] != 0; ++index)
    res %= final_value(list[index]);
  return (atom_res(INTEGER, res));
}
