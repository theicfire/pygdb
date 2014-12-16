test:
	LD_LIBRARY_PATH=`pwd`/cyout:$LD_LIBRARY_PATH py.test tests.py -s

testwatch:
	while true; do inotifywait -e modify *.py || make test; done
interactive:
	LD_LIBRARY_PATH=`pwd`/cyout:$LD_LIBRARY_PATH python run.py

run-fns:
	LD_LIBRARY_PATH=`pwd`/cyout:$LD_LIBRARY_PATH python use.py
