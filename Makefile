.PHONY: help setup install test run clean

help:
	@echo "LLM CLI Tool - Available commands:"
	@echo ""
	@echo "  make setup       - Initial setup (create venv, install deps)"
	@echo "  make install     - Install dependencies"
	@echo "  make test        - Run configuration tests"
	@echo "  make run         - Run the CLI tool"
	@echo "  make clean       - Clean cache files"
	@echo "  make format      - Format code with black (if installed)"
	@echo ""

setup:
	@bash setup.sh

install:
	pip install -r requirements.txt

test:
	python3 test_config.py

run:
	python3 main.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -f .chat_history
	@echo "✓ Cleaned up cache files"

format:
	black *.py

dev-setup: setup test
	@echo "✓ Development environment ready!"
	@echo "Run 'make run' to start the CLI"
