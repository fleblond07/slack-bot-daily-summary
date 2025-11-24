.PHONY: up down build logs restart test test-db-up test-db-down run shell

up:
	doppler run -- docker-compose up -d

down:
	docker-compose down

build:
	doppler run -- docker-compose build

run:
	doppler run -- uv run uvicorn endpoint:app --host 0.0.0.0 --port 8000

test:
	doppler run -c test -- uv run pytest tests/ -v
