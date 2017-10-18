#include "list.h"
#include <vector>

struct list_buf_e
{
	std::vector<const char*>	_v;
};

extern "C"
list_buf_t *list_new()
{
	return new list_buf_e();
}

extern "C"
void list_clean(list_buf_t *l)
{
	delete l;
}

extern "C"
void 			list_append(list_buf_t *l, const char *s)
{
	l->_v.push_back(s);
}

extern "C"
unsigned long	list_len(list_buf_t *l)
{
	return l->_v.size();
}

extern "C"
const char 		*list_nth(list_buf_t *l, unsigned long idx)
{
	return l->_v[idx];
}
