.PHONY: help up down build migrate makemigrations seed test lint format shell createsuperuser logs clean

help:
	@echo "Medicine ERP - Makefile Commands"
	@echo "================================="
	@echo "up              - Start all services"
	@echo "down            - Stop all services"
	@echo "build           - Build Docker images"
	@echo "migrate         - Run Django migrations"
	@echo "makemigrations  - Create Django migrations"
	@echo "seed            - Seed database with initial data"
	@echo "test            - Run tests"
	@echo "lint            - Run linters"
	@echo "format          - Format code"
	@echo "shell           - Open Django shell"
	@echo "createsuperuser - Create Django superuser"
	@echo "logs            - Show logs"
	@echo "clean           - Clean up containers and volumes"

up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose build

migrate:
	docker-compose exec backend python manage.py migrate

makemigrations:
	docker-compose exec backend python manage.py makemigrations

seed:
	docker-compose exec backend python manage.py seed_initial_data
	docker-compose exec backend python manage.py seed_services
	docker-compose exec backend python manage.py seed_staff
	docker-compose exec backend python manage.py seed_patients
	docker-compose exec backend python manage.py seed_appointments

test:
	docker-compose exec backend pytest

lint:
	docker-compose exec backend ruff check .
	docker-compose exec backend black --check .
	docker-compose exec backend isort --check-only .

format:
	docker-compose exec backend black .
	docker-compose exec backend isort .
	docker-compose exec backend ruff check --fix .

shell:
	docker-compose exec backend python manage.py shell

createsuperuser:
	docker-compose exec backend python manage.py createsuperuser

logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

clean:
	docker-compose down -v
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

