all: env
	. env/bin/activate && python main.py

env:
	virtualenv env
	. env/bin/activate && pip install Twisted requests

test:
	. env/bin/activate && trial test

.PHONY: test