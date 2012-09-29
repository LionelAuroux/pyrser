#ifndef __LISP__
#define __LISP__

typedef enum		e_bool
{
  false,
  true
}			bool;

typedef enum		e_atom_type
{
  BOOLEAN,
  FUNCTOR,
  LIST,
  IDENTIFIER,
  INTEGER,
  STRING,
}			atom_type;

typedef	struct		t_atom
{
  atom_type		kind;
  void*			value;
}			atom;

typedef struct		t_integer
{
  atom_type		kind;
  long int		value;
}			s_integer;

typedef struct		t_functor
{
  atom_type		kind;
  const atom*  		(*func)(const atom**);
  const atom**		args;
}			s_functor;

#define	ARRAY(...) 		(const atom*[]){__VA_ARGS__, 0x0}

#define __atom(kind, value)	&(atom){kind, (void*) value}
#define type(atom)			atom->kind

#define integer(value) 		__atom(INTEGER, value)
#define integer_value(atom) 	(((const s_integer*)atom)->value)

#define boolean(value)		__atom(BOOLEAN, value)

#define id(value) 		__atom(IDENTIFIER, value)
#define id_value(atom) 		((const char*)atom->value)

#define string(value) 		__atom(STRING, value)
#define string_value(atom) 	((const char*)atom->value)

#define list(...) 		__atom(LIST, ARRAY(__VA_ARGS__))
#define list_value(list)	((const atom**)list->value)

#define functor(func, ...)\
	(atom*)&(s_functor){FUNCTOR\
			  ,(void*)__##func\
			  ,ARRAY(__VA_ARGS__)}

#define exec_functor(functor)\
	((const s_functor*)functor)->func(((const s_functor*)functor)->args)

#define fdecl(name, ...)\
	final_value(__##name(ARRAY(__VA_ARGS__)))

long int	final_value(const atom* atom);
const atom*	atom_res(atom_type type, long int value);

#endif /* __LISP__ */
