export LD_LIBRARY_PATH = $(shell echo `pwd`/cyout:`pwd`/cyout/32:`pwd`/cyout/64:$$LD_LIBRARY_PATH)
export LIBRARY_PATH=$(LD_LIBRARY_PATH)

cython/ptracelib/makedone: cython/ptracelib/*.c cython/ptracelib/*.h cython/ptracelib/*.pyx cython/ptracelib/*.py cython/ptracelib/*.asm
	cd cython/ptracelib && $(MAKE)
	touch cython/ptracelib/makedone
ptracelib: cython/ptracelib/makedone

cython/dwarflib/makedone: cython/dwarflib/*.c cython/dwarflib/*.h cython/dwarflib/*.pyx cython/dwarflib/*.py
	cd cython/dwarflib && $(MAKE) standard
	touch cython/dwarflib/makedone
dwarflib: cython/dwarflib/makedone

all: binary_programs dwarflib ptracelib

test: binary_programs
	py.test

test-s: binary_programs
	py.test -s

test-all: test
	# TODO dwarflib tests
	cd cython/ptracelib && $(MAKE) test


traced_c_loop: ptracelib
	cp cython/ptracelib/traced_c_loop .

hello: ptracelib
	cp cython/ptracelib/hello .

tracedprog2: dwarflib
	cp cython/dwarflib/tracedprog2 .

binary_programs: traced_c_loop tracedprog2 hello

testwatch:
	while true; do inotifywait -e modify *.py || $(MAKE) test; done
interactive:
	python run.py

sub-make: sub-clean
	cd cython/dwarflib && $(MAKE) standard && cd ../..
	cd cython/ptracelib && $(MAKE) py && cd ../..

sub-clean:
	cd cython/dwarflib && $(MAKE) clean && cd ../..
	cd cython/ptracelib && $(MAKE) clean && cd ../..

clean: sub-clean
	rm -rf __pycache__
	rm -f *.pyc
	rm -f tracedprog2 traced_c_loop hello
	rm -f cyout/libdebug.so cyout/libdwarf_get_func_addr.so cyout/use_debuglib.so cyout/use_dwarf.so
	rm -f cython/ptracelib/ptracebuilt
	rm -f cython/ptracelib/makedone cython/dwarflib/makedone
