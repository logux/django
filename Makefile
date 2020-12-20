.DEFAULT_GOAL := help
.PHONY: install deps run test ci_test build release clean release_test release_production lint lbt docs setup

## Init

install:  ## Install this pkg in editable (develop) mode
	poetry run dephell --version
	poetry run dephell project register --from=pyproject .

deps:  ## Install dev dependencies (global)
	poetry install

## Code quality

lint:  ## Lint and static-check code
	flake8 logux
	pylint logux
	mypy logux

lbt:  ## Run logux-backend integration tests
	cd tests/lbt && npx @logux/backend-test http://localhost:8000/logux/

lbt_deps:  ## Install @logux/backend-test from NPM
	cd tests/lbt && npm install

integration_test:  ## Up Django backend and run backend-test
	poetry run tests/manage.py migrate && poetry run tests/manage.py wipe_db
	poetry run tests/manage.py runserver --settings=tests.test_project.test_settings & echo $$! > django.PID
	sleep 3
	cd tests/lbt && npx @logux/backend-test http://localhost:8000/logux/ || echo "FAIL" > ../test_result.tmp

	if [ -a test_result.tmp ]; then \
		kill -TERM $$(cat django.PID); \
		rm -f test_result.tmp django.PID && exit 1; \
	fi;

	kill -TERM $$(cat django.PID)
	rm -f test_result.tmp django.PID

integration_test_ci:  ## Up Django backend and run backend-test
	export PYTHONPATH=$PYTHONPATH:$(pwd) && python tests/manage.py migrate && python tests/manage.py wipe_db
	export PYTHONPATH=$PYTHONPATH:$(pwd) && python tests/manage.py runserver --settings=tests.test_project.test_settings & echo $$! > django.PID
	sleep 3
	cd tests/lbt && npx @logux/backend-test http://localhost:8000/logux/ || echo "FAIL" > ../test_result.tmp

	if [ -a test_result.tmp ]; then \
		kill -TERM $$(cat django.PID); \
		rm -f test_result.tmp django.PID && exit 1; \
	fi;

	kill -TERM $$(cat django.PID)
	rm -f test_result.tmp django.PID

test:  ## Run tests (venv)
	poetry run tests/manage.py test test_app

ci_test:  ## Run tests inside CI ENV
	export PYTHONPATH=$PYTHONPATH:$(pwd) && python tests/manage.py test test_app

## Run

run:  ## Run local dev server (venv)
	poetry run tests/manage.py runserver

build: clean test lint setup  ## Build package
	poetry build

changelog:  ## Generate changelog
	conventional-changelog -p angular -i CHANGELOG.md -s

docs:  ## Run auto-docs build
	cd docs && poetry run make clean && poetry run make xml

## Release

release_test: build  ## Release package on test PyPI server
	poetry config repositories.test https://test.pypi.org/legacy/
	poetry publish -r test

release_production: build  ## Release package on PyPI server
	poetry publish

setup:  ## Convert pyproject to setup.py
	dephell deps convert

clean:  ## Remove cache
	rm -rf ./dist ./build ./logux_django.egg-info ./README.rst

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
