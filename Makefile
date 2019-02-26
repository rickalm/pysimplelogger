# vim:ft=make: 

_PYTHON_VERSION=3.6.6

all: test
valid: isValid

isPYENV:
	@echo --- entering $@
	@test -n "${PYENV_SHELL}" || echo 'pyenv is not part of your environment.. Please execute the following first\n\neval "$$(pyenv init -)"\n\n\n'
	@test -n "${PYENV_SHELL}"

env: isPYENV 
	@echo --- entering $@
	@pyenv install ${_PYTHON_VERSION} -s
	@pyenv local ${_PYTHON_VERSION}
	@poetry install

isValid: clean env
	@echo --- entering $@
	poetry check

clean: vdir=$(shell poetry debug:info | grep Path | cut -d: -f2- | sed -e 's/^ *//')
clean: clean_build
	@echo --- entering $@
	@-[ -n "${vdir}" ] && rm -rf ${vdir}
	@-rm -rf dist/ .python_version

clean_build:
	@echo --- entering $@
	@-find . -type d -name __pycache__ | xargs rm -rf
	@-rm -rf *.egg-info/ build/ .pytest_cache/

test: isValid
	@echo --- entering $@
	poetry run python -m pytest

build: test
	@echo --- entering $@
	poetry build

upload: build clean_build
	@echo --- entering $@
	poetry publish
