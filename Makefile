all: binary_programs

test: binary_programs
	LD_LIBRARY_PATH=`pwd`/cyout:$LD_LIBRARY_PATH py.test

test-s: binary_programs
	LD_LIBRARY_PATH=`pwd`/cyout:$LD_LIBRARY_PATH py.test -s

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
	LD_LIBRARY_PATH=`pwd`/cyout:$LD_LIBRARY_PATH python run.py

sub-make: sub-clean
	cd cython/dwarflib && make standard && cd ../..
	cd cython/ptracelib && make py && cd ../..

sub-clean:
	cd cython/dwarflib && make clean && cd ../..
	cd cython/ptracelib && make clean && cd ../..

run-fns:
	LD_LIBRARY_PATH=`pwd`/cyout:$LD_LIBRARY_PATH python use.py

clean: sub-clean
	rm -rf __pycache__
	rm -f *.pyc
	rm -f tracedprog2 traced_c_loop hello
