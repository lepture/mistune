.PHONY: clean-pyc clean-build docs

test:
	@pytest -s

coverage:
	@pytest --cov=mistune

clean: clean-build clean-pyc clean-docs

build:
	@python3 -m build

clean-build:
	@rm -fr build/
	@rm -fr dist/
	@rm -fr *.egg-info
	@rm -fr .coverage


clean-pyc:
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +
	@find . -name '__pycache__' -exec rm -fr {} +

clean-docs:
	@rm -fr  docs/_build

docs:
	@$(MAKE) -C docs html

publish:
	@twine upload dist/*.tar.gz
	@twine upload dist/*.whl

.PHONY: build
