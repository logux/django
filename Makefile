.PHONY: venv install run

venv:
	python3 -m venv env

install:
	env/bin/pip install -e .

run:
	./env/bin/python logux/manage.py runserver

#build:
#    python3 setup.py sdist bdist_wheel
#    twine check dist/*
