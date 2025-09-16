.PHONY: help install test lint format clean run docker-build docker-up docker-down migrate superuser loaddata

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt
	pre-commit install

test: ## Run tests
	pytest

test-cov: ## Run tests with coverage
	pytest --cov=. --cov-report=html --cov-report=term

lint: ## Run linting
	flake8 .
	pylint apps/ config/
	black --check .
	isort --check-only .

format: ## Format code
	black .
	isort .

clean: ## Clean up
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage

run: ## Run development server
	python manage.py runserver

migrate: ## Run migrations
	python manage.py makemigrations
	python manage.py migrate

superuser: ## Create superuser
	python manage.py create_superuser

loaddata: ## Load sample data
	python manage.py load_sample_data

collectstatic: ## Collect static files
	python manage.py collectstatic --noinput

docker-build: ## Build Docker image
	docker build -t django-rest-api .

docker-up: ## Start Docker services
	docker-compose up -d

docker-down: ## Stop Docker services
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f

docker-shell: ## Access Docker container shell
	docker-compose exec web bash

docker-migrate: ## Run migrations in Docker
	docker-compose exec web python manage.py migrate

docker-superuser: ## Create superuser in Docker
	docker-compose exec web python manage.py create_superuser

docker-loaddata: ## Load sample data in Docker
	docker-compose exec web python manage.py load_sample_data

setup: install migrate superuser loaddata ## Complete setup
	@echo "Setup complete! Run 'make run' to start the server."

ci: test lint format ## Run CI checks
