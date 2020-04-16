.PHONY: venv install run test build release clean

venv:
	python3 -m venv env

install:
	env/bin/pip install -e .

run:
	./env/bin/python tests/manage.py runserver

test:
	source env/bin/activate && python tests/manage.py test test_app

build: clean test
	python3 setup.py sdist bdist_wheel
	python3 -m twine check dist/*

release:
	python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

clean:
	rm -rf ./dist ./build