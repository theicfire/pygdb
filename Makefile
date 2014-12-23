export LD_LIBRARY_PATH = $(shell echo `pwd`/cyout:`pwd`/cyout/32:`pwd`/cyout/64:$$LD_LIBRARY_PATH)
export LIBRARY_PATH=$(LD_LIBRARY_PATH)

all: binary_programs dwarflib ptracelib

.ptrace_make_done: cython/ptracelib/*.c cython/ptracelib/*.h cython/ptracelib/*.pyx cython/ptracelib/*.py cython/ptracelib/*.asm
	cd cython/ptracelib && $(MAKE)
	touch .ptrace_make_done
ptracelib: .ptrace_make_done

.dwarflib_make_done: cython/dwarflib/*.c cython/dwarflib/*.h cython/dwarflib/*.pyx cython/dwarflib/*.py
	cd cython/dwarflib && $(MAKE) standard
	touch .dwarflib_make_done
dwarflib: .dwarflib_make_done


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

to_clean =
to_clean += __pycache__
to_clean += *.pyc
to_clean += tracedprog2 traced_c_loop hello
to_clean += cyout/libdebug.so cyout/libdwarf_get_func_addr.so cyout/use_debuglib.so cyout/use_dwarf.so
to_clean += cython/ptracelib/ptracebuilt
to_clean += .dwarflib_make_done .ptrace_make_done
.PHONY : clean
clean: 
	rm -rf $(to_clean)
	cd cython/dwarflib && $(MAKE) clean && cd ../..
	cd cython/ptracelib && $(MAKE) clean && cd ../..
