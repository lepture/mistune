.PHONY: clean-pyc clean-build docs

test:
	@nosetests -s

bench:
	@python tests/bench.py

coverage:
	@rm -f .coverage
	@nosetests --with-coverage --cover-package=mistune --cover-html

clean: clean-build clean-pyc clean-docs


clean-build:
	@rm -fr build/
	@rm -fr dist/
	@rm -fr *.egg-info
	@rm -f mistune.c
	@rm -fr cover/


clean-pyc:
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +
	@find . -name '__pycache__' -exec rm -fr {} +

clean-docs:
	@rm -fr  docs/_build

docs:
	@$(MAKE) -C docs html

rtd:
	curl -X POST http://readthedocs.org/build/mistune

publish:
	@twine upload dist/*.tar.gz
	@twine upload dist/*.whl

.PHONY: build
