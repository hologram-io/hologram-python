.PHONY: install test testAll clean

install:
	python setup.py install

test:
	pytest tests/Authentication tests/Event tests/MessageMode

testAll:
	pytest tests/

clean:
	find . -name '*.pyc' -exec rm --force {} +
