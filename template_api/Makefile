.PHONY: help install install-dev test lint format clean run docker-build docker-run

# Variables
PYTHON := python3.12
PIP := $(PYTHON) -m pip
PYTEST := pytest
BLACK := black
RUFF := ruff
MYPY := mypy
DOCKER_IMAGE := template-api

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install production dependencies
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

install-dev:  ## Install development dependencies
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements-dev.txt
	pre-commit install

test:  ## Run tests with coverage
	$(PYTEST) --cov=. --cov-report=html --cov-report=term-missing

test-fast:  ## Run tests without coverage
	$(PYTEST) -v

test-watch:  ## Run tests in watch mode
	$(PYTEST) -f

lint:  ## Run all linters
	$(BLACK) --check .
	$(RUFF) check .
	$(MYPY) . --ignore-missing-imports

format:  ## Format code with black and isort
	$(BLACK) .
	isort .
	$(RUFF) check --fix .

security:  ## Run security checks
	bandit -r . -f json -o bandit-report.json
	safety check

clean:  ## Clean temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/

run:  ## Run the application
	uvicorn main:app --reload --port 8000

run-prod:  ## Run in production mode
	uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

docker-build:  ## Build Docker image
	docker build -t $(DOCKER_IMAGE):latest .

docker-run:  ## Run Docker container
	docker run -p 8000:8000 --env-file .env $(DOCKER_IMAGE):latest

docker-shell:  ## Open shell in Docker container
	docker run -it --rm --env-file .env $(DOCKER_IMAGE):latest /bin/bash

pre-commit:  ## Run pre-commit hooks on all files
	pre-commit run --all-files

update-deps:  ## Update dependencies
	$(PIP) install --upgrade -r requirements.txt -r requirements-dev.txt

migration-create:  ## Create new migration (use: make migration-create MSG="description")
	alembic revision --autogenerate -m "$(MSG)"

migration-upgrade:  ## Apply migrations
	alembic upgrade head

migration-downgrade:  ## Rollback last migration
	alembic downgrade -1

shell:  ## Open Python shell with app context
	$(PYTHON) -i -c "from main import app; print('App loaded. Use `app` variable.')"
