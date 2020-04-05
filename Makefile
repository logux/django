.PHONY: venv install run run_logux_server run_logux_client run_all

venv:
	python3 -m venv env

install:
	env/bin/pip install -e .

run:
	./env/bin/python tests/manage.py runserver

run_logux_server:
	cd ./tests/server-logux/ && yarn start

run_logux_client:
	cd ./tests/client-logux/ && yarn start

run_all: run run_logux_server run_logux_client

# TODO: build to dist
#build:
#    python3 setup.py sdist bdist_wheel
#    twine check dist/*
