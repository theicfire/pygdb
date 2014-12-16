test:
	LD_LIBRARY_PATH=`pwd`/cyout:$LD_LIBRARY_PATH py.test tests.py
testwatch:
	while true; do inotifywait -e modify *.py || make test; done

run-fns:
	LD_LIBRARY_PATH=`pwd`/cyout:$LD_LIBRARY_PATH python use.py
