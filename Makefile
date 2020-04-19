.PHONY: venv install run test ci_test build release clean release_test release_production lint

venv:
	python3 -m venv env

install:
	env/bin/pip install -e .

run:
	./env/bin/python tests/manage.py runserver

test:
	./env/bin/python tests/manage.py test test_app

ci_test:
	python tests/manage.py test test_app

build: clean test lint
	python3 setup.py sdist bdist_wheel
	python3 -m twine check dist/*

release_test: build
	python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

release_production: build
	python3 -m twine upload dist/*

clean:
	rm -rf ./dist ./build ./logux_django.egg-info

lint:
	flake8 ./logux --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 ./logux --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
	mypy --config-file mypy.ini ./logux