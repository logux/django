.PHONY: venv install run test build release clean release_test release_production

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

release_test:
	python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

release_production:
	python3 -m twine upload dist/*

clean:
	rm -rf ./dist ./build ./logux_django.egg-info