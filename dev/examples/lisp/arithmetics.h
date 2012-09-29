#ifndef __ARITHMETICS__
#define __ARITHMETICS__

const atom*		__add(const atom**);
const atom*		__minus(const atom**);
const atom*		__time(const atom**);
const atom*		__divide(const atom**);
const atom*		__modulus(const atom**);

#define add(...) 	fdecl(add, __VA_ARGS__)
#define minus(...) 	fdecl(minus, __VA_ARGS__)
#define time(...) 	fdecl(time, __VA_ARGS__)
#define divide(...) 	fdecl(divide, __VA_ARGS__)
#define modulus(...) 	fdecl(modulus, __VA_ARGS__)

#endif /* __ARITHMETICS__ */
