LBITS := $(shell getconf LONG_BIT)
all: with_lib

test: clean debuglib traced_c_loop hello
	cp traced_c_loop tests/
	gcc -Wall -I. -L../../cyout -Wextra -std=c99 -o tests/test_all tests/test_all.c -ldebug
	LD_LIBRARY_PATH=`pwd`/../../cyout:$LD_LIBRARY_PATH ./tests/test_all

debuglib:
	#gcc -Wall -Wextra -std=c99 -O2 -c debuglib.c # Works for normal c
	gcc -Wall -fPIC -Wextra -std=c99 -c debuglib.c
	gcc -std=c99 -shared -o ../../cyout/libdebug.so debuglib.o

traced_c_loop:
	gcc -Wall -Wextra -std=c99 -o traced_c_loop traced_c_loop.c

py: debuglib traced_c_loop
	gcc -Wall -fPIC -Wextra -std=c99 -c debuglib.c
	gcc -std=c99 -shared -o ../../cyout/libdebug.so debuglib.o
	LDFLAGS="-L../../cyout/ -L." python setup.py build_ext --inplace
	cp use_debuglib.so ../../cyout/ # TODO better way

run-py:
	LD_LIBRARY_PATH=`pwd`/../../cyout:$LD_LIBRARY_PATH python use.py

with_lib: debuglib traced_c_loop
	gcc -Wall -Wextra -std=c99 -c bp_use_lib.c
	gcc -Wall -L../../cyout/ -Wextra -std=c99 -o bp_use_lib bp_use_lib.o -ldebug

run_with_lib: with_lib
	LD_LIBRARY_PATH=`pwd`/../../cyout:$LD_LIBRARY_PATH ./bp_use_lib traced_c_loop

hello:
ifeq ($(LBITS),64) # 64 bit
	nasm -f elf64 -o hello.o hello.asm
else # 32 bit
	nasm -f elf32 -o hello.o hello.asm
endif
	ld -o hello hello.o

.PHONY : clean
clean :
	rm -f *.o bp_use_lib traced_c_loop use_debuglib.c
	rm -rf build
	rm -f hello
	rm -f *.so
	rm -f tests/traced_c_loop tests/test_all