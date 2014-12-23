all: tracedprog2

tracedprog2:
	gcc -Wall -Wextra -std=c99 -g -o tracedprog2 tracedprog2.c

run: all
	./dwarf_get_func_addr tracedprog2

justc: tracedprog2
	gcc -std=c99 -Wall -L../../cyout/ -fPIC -o dwarf.out dwarf_get_func_addr.c -ldwarf -lelf
	LD_LIBRARY_PATH=`pwd`/../../cyout:$LD_LIBRARY_PATH ./dwarf.out tracedprog2

valgrind: all
	LD_LIBRARY_PATH=`pwd`/../../cyout:$LD_LIBRARY_PATH valgrind ./dwarf.out tracedprog2

standard: all
	gcc -std=c99 -Wall -fPIC -c dwarf_get_func_addr.c
	gcc -shared -o ../../cyout/libdwarf_get_func_addr.so dwarf_get_func_addr.o
	LDFLAGS="-L../../cyout/ -L." python setup.py build_ext --inplace
	cp use_dwarf.so ../../cyout/ # TODO can be done in setup.py? Or call setup.py from diff dir?

run-standard: standard
	LD_LIBRARY_PATH=`pwd`/../../cyout:$LD_LIBRARY_PATH python use.py


.PHONY : clean
clean : 
	rm -rf tracedprog2 dwarf_get_func_addr
	rm -f use_dwarf.c *.so helloworld.c dwarf.out
	rm -rf build
	rm -f *.a
	rm -f *.o
