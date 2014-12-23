export LD_LIBRARY_PATH = $(shell echo `pwd`/cyout:`pwd`/cyout/32:`pwd`/cyout/64:$$LD_LIBRARY_PATH)
export LIBRARY_PATH=$(LD_LIBRARY_PATH)

all: binary_programs

test: binary_programs
	py.test

test-s: binary_programs
	py.test -s

test-all: test
	# TODO dwarflib tests
	cd cython/ptracelib && $(MAKE) test


traced_c_loop:
	cd cython/ptracelib && $(MAKE) traced_c_loop
	cp cython/ptracelib/traced_c_loop .

hello:
	cd cython/ptracelib && $(MAKE) hello
	cp cython/ptracelib/hello .

tracedprog2:
	cd cython/dwarflib && $(MAKE) tracedprog2
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
