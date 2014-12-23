export LD_LIBRARY_PATH = $(shell echo `pwd`/cyout:`pwd`/cyout/32:`pwd`/cyout/64:$$LD_LIBRARY_PATH)
export LIBRARY_PATH=$(LD_LIBRARY_PATH)

all: binary_programs

test: binary_programs
	py.test

test-s: binary_programs
	py.test -s

test-all: test
	# TODO dwarflib tests
	cd cython/ptracelib && make test


traced_c_loop:
	cd cython/ptracelib && make traced_c_loop
	cp cython/ptracelib/traced_c_loop .

hello:
	cd cython/ptracelib && make hello
	cp cython/ptracelib/hello .

tracedprog2:
	cd cython/dwarflib && make tracedprog2
	cp cython/dwarflib/tracedprog2 .

binary_programs: traced_c_loop tracedprog2 hello

testwatch:
	while true; do inotifywait -e modify *.py || make test; done
interactive:
	python run.py

sub-make: sub-clean
	cd cython/dwarflib && make standard && cd ../..
	cd cython/ptracelib && make py && cd ../..

sub-clean:
	cd cython/dwarflib && make clean && cd ../..
	cd cython/ptracelib && make clean && cd ../..

run-fns:
	python use.py

clean: sub-clean
	rm -rf __pycache__
	rm -f *.pyc
	rm -f tracedprog2 traced_c_loop hello
	rm -f cyout/libdebug.so cyout/libdwarf_get_func_addr.so cyout/use_debuglib.so cyout/use_dwarf.so
