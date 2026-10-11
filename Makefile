.PHONY: build up down logs shell test migrate seed lint format

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

shell-api:
	docker-compose exec api /bin/sh

shell-worker:
	docker-compose exec worker /bin/sh

test:
	docker-compose exec api pytest -xvs

migrate:
	docker-compose exec api alembic upgrade head

makemigrations:
	docker-compose exec api alembic revision --autogenerate -m "auto migration"

seed:
	docker-compose exec api python scripts/seed.py

lint:
	docker-compose exec api flake8 app tests
	docker-compose exec api mypy app

format:
	docker-compose exec api black app tests
	docker-compose exec api isort app tests

clean:
	docker-compose down -v
	docker system prune -f
