export LD_LIBRARY_PATH = $(shell echo `pwd`/../../cyout:`pwd`/../../cyout/32:`pwd`/../../cyout/64:$$LD_LIBRARY_PATH)
export LIBRARY_PATH=$(LD_LIBRARY_PATH)

all: tracedprog2

tracedprog2:
	gcc -Wall -Wextra -std=c99 -g -o tracedprog2 tracedprog2.c

run: all
	./dwarf_get_func_addr tracedprog2

justc: tracedprog2
	gcc -std=c99 -Wall -fPIC -o dwarf.out dwarf_get_func_addr.c -ldwarf -lelf
	./dwarf.out tracedprog2

valgrind: all
	valgrind ./dwarf.out tracedprog2

standard: all
	gcc -std=c99 -Wall -fPIC -c dwarf_get_func_addr.c
	gcc -shared -o ../../cyout/libdwarf_get_func_addr.so dwarf_get_func_addr.o
	LDFLAGS="-L../../cyout/ -L." python setup.py build_ext --inplace
	cp use_dwarf.so ../../cyout/ # TODO can be done in setup.py? Or call setup.py from diff dir?

to_clean =
to_clean += tracedprog2 dwarf_get_func_addr
to_clean += use_dwarf.c *.so helloworld.c dwarf.out
to_clean += build
to_clean += *.a
to_clean += *.o
.PHONY : clean
clean : 
	rm -rf $(to_clean)
