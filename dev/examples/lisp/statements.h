#ifndef __STATEMENTS__
#define __STATEMENTS__

const atom*		__condition(const atom**);
const atom*		__print(const atom**);

#define condition(...) 	__condition(ARRAY(__VA_ARGS__))
#define print(...) 	__print(ARRAY(__VA_ARGS__))

#endif /* __STATEMENTS__ */
