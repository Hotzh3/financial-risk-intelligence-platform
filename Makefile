SHELL := /bin/zsh

PYTHON := $(shell if [ -x .venv/bin/python ]; then echo .venv/bin/python; else echo python3; fi)
PIP := $(shell if [ -x .venv/bin/pip ]; then echo .venv/bin/pip; else echo pip3; fi)

.PHONY: help install test api dashboard demo demo-docker docker-build docker-up docker-down docker-logs clean

help:
	@echo "Available targets:"
	@echo "  make install      - create venv (if missing) and install dependencies"
	@echo "  make test         - run pytest"
	@echo "  make api          - run FastAPI service on :8000"
	@echo "  make dashboard    - run Streamlit dashboard on :8501"
	@echo "  make demo         - run API + dashboard from one terminal"
	@echo "  make demo-docker  - run API + dashboard with Docker Compose"
	@echo "  make docker-build - build Docker images"
	@echo "  make docker-up    - start API + dashboard with Docker Compose"
	@echo "  make docker-down  - stop Docker Compose services"
	@echo "  make docker-logs  - tail Docker Compose logs"
	@echo "  make clean        - remove Python cache artifacts"

install:
	@if [ ! -d .venv ]; then python3 -m venv .venv; fi
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt

test:
	$(PYTHON) -m pytest -q

api:
	$(PYTHON) -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000

dashboard:
	$(PYTHON) -m streamlit run dashboard/app.py --server.address=0.0.0.0 --server.port=8501

demo:
	bash scripts/run_demo.sh

demo-docker:
	docker compose up --build

docker-build:
	docker compose build

docker-up:
	docker compose up --build

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
