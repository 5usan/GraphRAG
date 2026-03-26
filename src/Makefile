.PHONY: run dev help clean

help:
	@echo "Available targets:"
	@echo "  make run  - Start FastAPI server in production mode"
	@echo "  make dev  - Start FastAPI server with auto-reload"
	@echo "  make clean - Remove cache and build files"

run:
	uvicorn main:app --host 0.0.0.0 --port 8000

dev:
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
