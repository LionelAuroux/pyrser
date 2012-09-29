CC	=	clang

CFLAGS	=	-Wall -Wextra -g3

SRCS	=	lisp.c arithmetics.c statements.c booleans.c

MAIN	=	main.c

TEST	=	test.c

OBJS	=	$(SRCS:.c=.o) $(MAIN:.c=.o)

TESTOBJS=	$(SRCS:.c=.o) $(TEST:.c=.o)

all:	$(OBJS)
	$(CC) $(OBJS)

test:	$(TESTOBJS)
	$(CC) $(TESTOBJS)
	./a.out

clean:
	rm -rf $(OBJS)
	rm -rf $(TESTOBJS)

fclean:	clean
	rm -rf ./a.out

re: fclean all

retest: fclean test
