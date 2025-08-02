.PHONY: test test-unit test-coverage lint format clean install dev-install help

PYTHON := python3
PIP := $(PYTHON) -m pip
PYTEST := $(PYTHON) -m pytest
UNITTEST := $(PYTHON) -m unittest

GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m

help: ## Show help
	@echo "$(GREEN)🛠️  Docker Tool - Available commands$(NC)"
	@echo "============================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Install production dependencies
	@echo "$(GREEN)📦 Installing production dependencies$(NC)"
	$(PIP) install -e .

dev-install: ## Install development dependencies
	@echo "$(GREEN)🔧 Installing development dependencies$(NC)"
	$(PIP) install -e .
	$(PIP) install pytest pytest-cov pytest-mock coverage black flake8 mypy

test-unit: ## Run unit tests (no dependencies)
	@echo "$(GREEN)🧪 Unit tests (unittest)$(NC)"
	$(UNITTEST) discover tests -p "test_unittest.py" -v

test: ## Run all tests with pytest
	@echo "$(GREEN)🔬 Complete tests (pytest)$(NC)"
	$(PYTEST) tests/ -v

test-coverage: ## Run tests with coverage
	@echo "$(GREEN)📊 Tests with coverage$(NC)"
	$(PYTEST) tests/ --cov=docker_tool --cov-report=term-missing --cov-report=html:htmlcov --cov-fail-under=80

test-ci: ## Tests for CI (unittest only)
	@echo "$(GREEN)🚀 CI Tests$(NC)"
	$(UNITTEST) discover tests -p "test_unittest.py" -v

lint: ## Check code with flake8
	@echo "$(GREEN)🔍 Code checking$(NC)"
	$(PYTHON) -m flake8 docker_tool tests --max-line-length=100 --exclude=__pycache__

format: ## Format code with black
	@echo "$(GREEN)✨ Code formatting$(NC)"
	$(PYTHON) -m black docker_tool tests --line-length=100

type-check: ## Type checking with mypy
	@echo "$(GREEN)🔎 Type checking$(NC)"
	$(PYTHON) -m mypy docker_tool --ignore-missing-imports

clean: ## Clean temporary files
	@echo "$(GREEN)🧹 Cleaning$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf htmlcov/ .coverage .pytest_cache/ .mypy_cache/

build: ## Build package
	@echo "$(GREEN)📦 Building package$(NC)"
	$(PYTHON) -m build

publish-test: build ## Publish to TestPyPI
	@echo "$(GREEN)🚀 Publishing to TestPyPI$(NC)"
	$(PYTHON) -m twine upload --repository testpypi dist/*

publish: build ## Publish to PyPI
	@echo "$(GREEN)🚀 Publishing to PyPI$(NC)"
	$(PYTHON) -m twine upload dist/*

check: lint type-check test-unit ## Complete check (lint + types + tests)

all: clean dev-install check test-coverage ## Complete installation and tests
