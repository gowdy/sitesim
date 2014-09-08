PYTHONPATH:=$(PWD)/python

SOURCE=$(wildcard python/*.py)
TEST=$(wildcard test/*_t.py)

tests: $(TEST) $(SOURCE)
	@cd test
	@export PYTHONPATH=$(PYTHONPATH)
	@for test in $(TEST); do \
		python $$test; \
	done
	@cd ..

