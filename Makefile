# PGxRx Makefile
# Quick commands for development, testing, and deployment

.PHONY: install dev install-api test lint format clean docker docker-run help

help: ## Show this help
	@echo "PGxRx Makefile targets:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

install: ## Install package with all extras
	pip install -e ".[all]"

dev: install ## Install dev dependencies
	pip install -e ".[dev]"

test: ## Run all tests
	python -m pytest tests/ -v --tb=short --cov=pgxrx --cov-report=term-missing

test-quick: ## Run tests without coverage
	python -m pytest tests/ -v --tb=short

lint: ## Run linting
	ruff check pgxrx/ tests/
	ruff format --check pgxrx/ tests/

format: ## Format code
	ruff format pgxrx/ tests/
	ruff check pgxrx/ tests/ --fix

docker: ## Build Docker image
	docker build -t pgxrx:latest .

docker-run: ## Run Docker container
	docker run -p 8000:8000 pgxrx:latest server

docker-test: ## Run tests in Docker
	docker run --rm pgxrx:latest pytest tests/

clean: ## Remove build artifacts
	rm -rf build/ dist/ *.egg-info .pytest_cache .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete

serve: ## Start FastAPI dev server
	uvicorn pgxrx.api.server:app --host 0.0.0.0 --port 8000 --reload

build: ## Build distribution packages
	python -m build
