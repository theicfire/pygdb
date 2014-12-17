test:
	LD_LIBRARY_PATH=`pwd`/cyout:$LD_LIBRARY_PATH py.test

test-s:
	LD_LIBRARY_PATH=`pwd`/cyout:$LD_LIBRARY_PATH py.test -s

testwatch:
	while true; do inotifywait -e modify *.py || make test; done
interactive:
	LD_LIBRARY_PATH=`pwd`/cyout:$LD_LIBRARY_PATH python run.py

sub-make:
	cd cwrappin/cython_set_breakpoint && make clean && make py && cd ../..
	cd cwrappin/cython_get_fns && make clean && make standard && cd ../..

run-fns:
	LD_LIBRARY_PATH=`pwd`/cyout:$LD_LIBRARY_PATH python use.py

clean:
	rm -rf __pycache__
	rm -f *.pyc
