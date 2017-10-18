srcc = parser.c
srcxx = list.cc map.cc
objc = ${src:.c=.o}
objcxx = ${src:.cc=.o}

test = parser

all: ${objc} ${objcxx}
	@echo Done

debug: ${objcxx}
	@echo Compilation des TUs
	@gcc -DDEBUG -g ${srcc} ${objcxx} -o ${test}

clean:
	@rm -f *.swp *~ *.o

distclean: clean
	@rm -f ${test}
