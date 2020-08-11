.DEFAULT_GOAL := help
.PHONY: venv install deps run test ci_test build release clean release_test release_production lint lbt docs

## Init

venv:  ## Init VENV
	python3 -m venv env

install:  ## Install this pkg by setup.py (venv)
	env/bin/pip install -e .

deps:  ## Install dev dependencies (global)
	pip install black coverage flake8 mccabe mypy django-stubs pylint

## Code quality

lint:  ## Lint and static-check code
	flake8 logux
	pylint logux
	mypy logux

lbt:  ## Run logux-backend integration tests
	cd lbt && npx @logux/backend-test http://localhost:8000/logux/

integration_test:  ## Up Django backend and run backend-test
	./env/bin/python tests/manage.py migrate && ./env/bin/python tests/manage.py wipe_db
	./env/bin/python tests/manage.py runserver --settings=tests.test_project.test_settings & echo $$! > django.PID
	sleep 3
	cd lbt && npx @logux/backend-test http://localhost:8000/logux/ || echo "FAIL" > ../test_result.tmp

	if [ -a test_result.tmp ]; then \
		kill -TERM $$(cat django.PID); \
		rm -f test_result.tmp django.PID && exit 1; \
	fi;

	kill -TERM $$(cat django.PID)
	rm -f test_result.tmp django.PID

test:  ## Run tests (venv)
	./env/bin/python tests/manage.py test test_app

ci_test:  ## Run tests inside CI ENV
	export PYTHONPATH=$PYTHONPATH:$(pwd) && python tests/manage.py test test_app

## Run

run:  ## Run local dev server (venv)
	./env/bin/python tests/manage.py runserver


build: clean test lint  ## Build package
	python3 setup.py sdist bdist_wheel
	python3 -m twine check dist/*

changelog:  ## Generate changelog
	conventional-changelog -p angular -i CHANGELOG.md -s

docs:  ## Run auto-docs build
	. env/bin/activate && cd docs && make clean && make html

## Release

release_test: build  ## Release package on test PyPI server
	python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

release_production: build  ## Release package on PyPI server
	python3 -m twine upload dist/*

clean:  ## Remove cache
	rm -rf ./dist ./build ./logux_django.egg-info

## Help

help: ## Show help message
	@IFS=$$'\n' ; \
	help_lines=(`fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##/:/'`); \
	printf "%s\n\n" "Usage: make [task]"; \
	printf "%-20s %s\n" "task" "help" ; \
	printf "%-20s %s\n" "------" "----" ; \
	for help_line in $${help_lines[@]}; do \
		IFS=$$':' ; \
		help_split=($$help_line) ; \
		help_command=`echo $${help_split[0]} | sed -e 's/^ *//' -e 's/ *$$//'` ; \
		help_info=`echo $${help_split[2]} | sed -e 's/^ *//' -e 's/ *$$//'` ; \
		printf '\033[36m'; \
		printf "%-20s %s" $$help_command ; \
		printf '\033[0m'; \
		printf "%s\n" $$help_info; \
	done
