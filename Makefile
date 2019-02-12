# vim:ft=make: 

dist_clean: clean
	rm -rf dist/

clean:
	rm -rf *.egg-info/ build/ .pytest_cache/
	find . -type d -name __pycache__ | xargs rm -rf

dist: dist_clean
	pipenv --rm
	pipenv run pipenv install -d
	pipenv run py.test
	pipenv run python3 setup.py sdist bdist_wheel
	make clean

test: dist_clean
	pipenv --rm
	pipenv run pipenv install -d
	pipenv run py.test

upload: dist
	pipenv run twine upload dist/*
