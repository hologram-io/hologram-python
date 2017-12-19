.PHONY: install test clean

install:
	python setup.py install

test:
	pytest tests/

clean:
	find . -name '*.pyc' -exec rm --force {} +
