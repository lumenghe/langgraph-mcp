.PHONY: clean clean-build clean-pyc clean-test clean-logs help
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test clean-logs ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -rf {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache
	rm -fr .coverage*
	rm -fr .tox/
	rm -fr .nox/

clean-logs: ## remove log files
	find . -name '*.log' -exec rm -f {} +
	find . -name '*.tmp' -exec rm -f {} +

ruff: ## check code with ruff
	ruff check .

ruff-fix: ## fix code issues with ruff
	ruff check --fix .

flake: ## check style with flake8
	flake8 .

format: ## format code with isort and black
	isort . --line-length 120
	black --target-version py311 . --line-length 120

format-check: ## check if code is formatted correctly
	isort . --line-length 120 --check-only
	black --target-version py311 . --line-length 120 --check

mypy: ## run type checking with mypy
	mypy .

lint: ruff flake mypy ## run all linting tools

test: ## run tests
	python -m pytest

test-verbose: ## run tests with verbose output
	python -m pytest -v

test-coverage: ## run tests with coverage
	python -m pytest --cov=. --cov-report=html --cov-report=term

run-client: ## run the client
	python client_langgraph.py

run-deals-server: ## run the deals MCP server
	python get_top_deals_by_spend.py

run-domains-server: ## run the domains MCP server
	python get_top_or_least_domains.py

install: ## install dependencies
	pip install -r requirements.txt

install-dev: ## install development dependencies
	pip install -r requirements-dev.txt

freeze: ## freeze current dependencies
	pip freeze > requirements.txt

venv: ## create virtual environment
	python -m venv venv
	@echo "Activate with: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)"

setup: venv install ## setup development environment
	@echo "Setup complete. Don't forget to activate your virtual environment!"

check: format-check lint test ## run all checks (format, lint, test)

