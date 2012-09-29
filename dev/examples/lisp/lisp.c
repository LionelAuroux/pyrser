#include <stdio.h>
#include <stdlib.h>
#include "lisp.h"

/*
static long int set_value(const char* identifier, const atom* atom)
{
  // if type(atom) == IDENTIFIER;
  // essayer de choper la valeur existante
  // else if type(atom) == INTEGER
}

static long int	fetch_value(const char* identifier)
{
  ;
}
*/

long int	final_value(const atom* atom)
{
  if (type(atom) == INTEGER || type(atom) == BOOLEAN)
    return integer_value(atom);
  else if (type(atom) == IDENTIFIER)
    return (0); // replace by get_constant(id_value(atom));
  else if (type(atom) == FUNCTOR)
    return (final_value(exec_functor(atom)));
  printf("Error : no final value possible\n");
  exit(1);
  return (false);
}

static atom 	final_res = {0, 0};

const atom*	atom_res(atom_type type, long int value)
{
  final_res.kind = type;
  final_res.value = (void*)value;
  return (&final_res);
}

#include <stdio.h>

void		dump_list(const atom* expr)
{
  int		index;
  const const atom**  real_expr;

  real_expr = list_value(expr);
  printf("(");
  for (index = 0; real_expr[index] != 0; ++index)
    {
      if (index > 0)
	printf(" ,");
      if (real_expr[index]->kind == INTEGER)
	printf("%ld", integer_value(real_expr[index]));
      if (real_expr[index]->kind == IDENTIFIER)
	printf("%s", id_value(real_expr[index]));
      if (real_expr[index]->kind == LIST)
	dump_list(real_expr[index]);
    }
  printf(")");
}
