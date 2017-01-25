.PHONY: install test testAll clean

install:
	python setup.py install

test:
	pytest tests -k 'not tests/Network'

testAll:
	pytest tests/

clean:
	find . -name '*.pyc' -exec rm --force {} +
