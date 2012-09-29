#ifndef __BOOLEANS__
#define __BOOLEANS__

const atom*				__and(const atom**);
const atom*				__or(const atom**);
const atom*				__not(const atom**);
const atom*				__equal(const atom**);
const atom*				__different(const atom**);
const atom*				__less(const atom**);
const atom*				__greater(const atom**);
const atom*				__less_or_equal(const atom**);
const atom*				__greater_or_equal(const atom**);

#define and(...) 		fdecl(and, __VA_ARGS__)
#define or(...) 		fdecl(or, __VA_ARGS__)
#define not(...) 		fdecl(not, __VA_ARGS__)
#define equal(...) 		fdecl(equal, __VA_ARGS__)
#define different(...) 		fdecl(different, __VA_ARGS__)
#define less(...) 		fdecl(less, __VA_ARGS__)
#define greater(...) 		fdecl(greater, __VA_ARGS__)
#define less_or_equal(...) 	fdecl(less_or_equal, __VA_ARGS__)
#define greater_or_equal(...) 	fdecl(greater_or_equal, __VA_ARGS__)

#endif /* __BOOLEANS__ */
