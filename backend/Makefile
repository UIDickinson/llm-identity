.PHONY: help install test lint format clean run dev

help:
	@echo "Provenance Guardian Backend - Makefile Commands"
	@echo ""
	@echo "  install     Install dependencies"
	@echo "  test        Run tests"
	@echo "  lint        Run linters"
	@echo "  format      Format code"
	@echo "  clean       Clean generated files"
	@echo "  run         Run production server"
	@echo "  dev         Run development server"
	@echo "  check       Check setup"

install:
	pip install -r requirements.txt
	DS_BUILD_OPS=1 pip install deepspeed

test:
	pytest tests/ -v

test-integration:
	pytest tests/ -v -m integration

lint:
	flake8 agent/ api/ models/ fingerprints/ utils/
	mypy agent/ api/ models/ fingerprints/ utils/ --ignore-missing-imports

format:
	black agent/ api/ models/ fingerprints/ utils/ tests/
	isort agent/ api/ models/ fingerprints/ utils/ tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf dist/
	rm -rf build/

run:
	python main.py

dev:
	uvicorn api.server:app --reload --host 0.0.0.0 --port 8000

check:
	python scripts/check_setup.py