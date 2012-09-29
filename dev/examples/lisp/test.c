#include <assert.h>
#include <stdio.h>
#include "lisp.h"
#include "arithmetics.h"
#include "booleans.h"
#include "statements.h"

int 		main(void)
{
  printf("----------------------------------------------------------\n");
  // Simple arithmetics

  assert(add(integer(42)) == 42); // (+ 42)
  assert(add(integer(40), integer(2)) == 42); // (+ 40 2)
  assert(add(integer(38), integer(2), integer(2)) == 42); // (+ 38 2 2)
  assert(minus(integer(40), integer(2)) == 38); // (- 38 2 2)
  assert(time(integer(40), integer(2)) == 80); // (* 40 2)
  assert(divide(integer(40), integer(2)) == 20); // (/ 40 2)
  assert(modulus(integer(40), integer(2)) == 0); // (% 40 2)
  
  // Functor arithmetics.
  // (+ 40 (+ 1 (+ 1 2 3)))
  assert(add(integer(40),
		     functor(add, integer(1),
		     functor(add, integer(1), integer(2), integer(3)))) == 47);
  // Booleans.
  // (&& (= 1 1) (= 4 4))

  assert(and(functor(equal, integer(1), integer(1)),
		  functor(equal, integer(4), integer(4))) == true);
  
  // (|| (= 1 2) (= 2 2))
  assert(or(functor(equal, integer(1), integer(2)),
	    functor(equal, integer(2), integer(2))) == true);
  
  // (! false)
  assert(not(integer(false)) == true);
  
  // (! true)
  assert(not(integer(true)) == false);
  
  // (= 1 1)
  assert(equal(integer(1), integer(1)) == true);
  
  // (= 0 1)
  assert(equal(integer(0), integer(1)) == false);

  // (!= 2 1)
  assert(different(integer(2), integer(1)) == true);

  // (!= 2 2)
  assert(different(integer(2), integer(2)) == false);

  // (< 1 2)
  assert(less(integer(1), integer(2)) == true);

  // (> 3 2)
  assert(greater(integer(3), integer(2)) == true);
  
  // (<= 1 1)
  assert(less_or_equal(integer(1), integer(1)) == true);
  
  // (>= 3 3)
  assert(greater_or_equal(integer(3), integer(3)) == true);

  // Statements.
  // (if (< 1 3)
  // 	 (print ">")
  //  (print "<"))

  condition(functor(less, integer(1), integer(3))
	   ,functor(print, string(">"))
	   ,functor(print, string("<")));

  // Statements.
  // (if (< 3 3)
  // 	 (print ">")

  condition(functor(less, integer(3), integer(3))
	   ,functor(print, string(">")));

  //(or
  //   (and (= 0 n) (print "n is null"))
  //(print "n is not null"))
  or(functor(and, functor(equal, integer(0), id("n")),
		  functor(print, string("n is null"))),
     functor(print, string("n is not null")));
  printf("All test passed\n");
  return 0;
}
