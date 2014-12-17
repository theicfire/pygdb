test:
	LD_LIBRARY_PATH=`pwd`/cyout:$LD_LIBRARY_PATH py.test

test-s:
	LD_LIBRARY_PATH=`pwd`/cyout:$LD_LIBRARY_PATH py.test -s

testwatch:
	while true; do inotifywait -e modify *.py || make test; done
interactive:
	LD_LIBRARY_PATH=`pwd`/cyout:$LD_LIBRARY_PATH python run.py

run-fns:
	LD_LIBRARY_PATH=`pwd`/cyout:$LD_LIBRARY_PATH python use.py
