# vim:ft=make: 

_PYTHON_VERSION=3.6.5

all: test

isPYENV:
	@echo --- entering $@
	@test -n "${PYENV_SHELL}"

isValid:
	@echo --- entering $@
	poetry check

env: isPYENV isValid
	@echo --- entering $@
	@pyenv install ${_PYTHON_VERSION} -s
	@pyenv local ${_PYTHON_VERSION}
	@poetry install

clean: vdir=$(shell poetry debug:info | grep Path | cut -d: -f2- | sed -e 's/^ *//')
clean: clean_build
	@echo --- entering $@
	@-[ -n "${vdir}" ] && rm -rf ${vdir}
	@-rm -rf dist/ .python_version

clean_build:
	@echo --- entering $@
	@-find . -type d -name __pycache__ | xargs rm -rf
	@-rm -rf *.egg-info/ build/ .pytest_cache/

test: isValid clean env
	@echo --- entering $@
	poetry run py.test

build: isValid test
	@echo --- entering $@
	poetry build
	make clean_build

upload: isValid build
	@echo --- entering $@
	poetry publish
