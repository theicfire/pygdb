test:
	py.test tests.py
testwatch:
	while true; do inotifywait -e modify *.py || make test; done
