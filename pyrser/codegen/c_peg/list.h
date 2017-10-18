#ifndef _LIST_H_
#define _LIST_H_

typedef struct list_buf_e list_buf_t;

// header commun C/C++
#ifdef __cplusplus
extern "C" {
#endif

list_buf_t *list_new();
void list_clean(list_buf_t *);

void 			list_append(list_buf_t *, const char *);
unsigned long	list_len(list_buf_t *);
const char 		*list_nth(list_buf_t *, unsigned long);

#ifdef __cplusplus
}
#endif

#endif
