.DEFAULT_GOAL := help

.PHONY: help setup api web test evaluate lint build

help:
	@echo "Available commands:"
	@echo "  make setup  Install backend and frontend dependencies"
	@echo "  make api    Start the FastAPI backend"
	@echo "  make web    Start the React frontend"
	@echo "  make test   Run backend tests"
	@echo "  make evaluate  Measure curated extraction accuracy"
	@echo "  make lint   Check frontend code quality"
	@echo "  make build  Build the production frontend"

setup:
	python3 -m venv .venv
	.venv/bin/python -m pip install --upgrade pip
	.venv/bin/python -m pip install -e .
	cd frontend && pnpm install

api:
	.venv/bin/python -m uvicorn app.api:app --host 127.0.0.1 --port 8000

web:
	cd frontend && pnpm dev

test:
	.venv/bin/python -m unittest discover -s tests -v

evaluate:
	.venv/bin/python -m scripts.evaluate_accuracy

lint:
	cd frontend && pnpm lint

build:
	cd frontend && pnpm build
