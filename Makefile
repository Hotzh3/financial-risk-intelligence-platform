SHELL := /bin/zsh

PYTHON := $(shell if [ -x .venv/bin/python ]; then echo .venv/bin/python; else echo python3; fi)
PIP := $(shell if [ -x .venv/bin/pip ]; then echo .venv/bin/pip; else echo pip3; fi)

.PHONY: install test api dashboard docker-build docker-up docker-down docker-logs clean

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
