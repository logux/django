.PHONY: venv install run test

venv:
	python3 -m venv env

install:
	env/bin/pip install -e .

run:
	./env/bin/python tests/manage.py runserver

test:
	source env/bin/activate && python tests/manage.py test test_app

# TODO: build to dist
#build:
#    python3 setup.py sdist bdist_wheel
#    twine check dist/*
