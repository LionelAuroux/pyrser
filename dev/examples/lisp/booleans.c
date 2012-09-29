#include "lisp.h"

const atom*		__equal(const atom** list)
{
  int			index;
  const atom*		current;

  current = list[0];
  for (index = 1; list[index] != 0; ++index)
    if (final_value(current) != final_value(list[index]))
      return (atom_res(BOOLEAN, false));
  return (atom_res(BOOLEAN, true));
}

const atom*		__different(const atom** list)
{
  return (atom_res(BOOLEAN, final_value(__equal(list)) == false));
}

const atom*		__and(const atom** list)
{
  int		index;
  
  for (index = 0; list[index] != 0; ++index)
    if (final_value(list[index]) == false)
      return (atom_res(BOOLEAN, false));
  return (atom_res(BOOLEAN, true));
}

const atom*		__or(const atom** list)
{
  int		index;
  
  for (index = 0; list[index] != 0; ++index)
    if (final_value(list[index]) == true)
      return (atom_res(BOOLEAN, true));
  return (atom_res(BOOLEAN, false));
}

const atom*		__not(const atom** list)
{
  return (atom_res(BOOLEAN, !final_value(list[0])));
}

const atom*		__less(const atom** list)
{
  return (atom_res(BOOLEAN, final_value(list[0]) < final_value(list[1])));
}

const atom*		__greater(const atom** list)
{
  return (atom_res(BOOLEAN, final_value(list[0]) > final_value(list[1])));
}

const atom*		__less_or_equal(const atom** list)
{
  return (atom_res(BOOLEAN, final_value(list[0]) <= final_value(list[1])));
}

const atom*		__greater_or_equal(const atom** list)
{
  return (atom_res(BOOLEAN, final_value(list[0]) >= final_value(list[1])));
}
