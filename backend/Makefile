# FastAPI Starter Template Makefile
# This Makefile provides commands for running tests and other common tasks

# Variables
PYTHON = python
TEST_DIR = tests
VENV_DIR = venv
VENV_ACTIVATE = . $(VENV_DIR)/bin/activate

# Default target
.PHONY: all
all: test

# Install dependencies
.PHONY: install
install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

# Run all tests
.PHONY: test
test:
	@echo "Running all tests..."
	@echo "\n=== Authentication Tests ===\n"
	$(MAKE) test-auth
	# Hello Authenticated Service Tests removed (now covered by integration tests)
	@echo "\n=== Integration Tests ===\n"
	$(MAKE) test-integration
	@echo "\n=== All tests completed successfully! ===\n"

# Run authentication test
.PHONY: test-auth
test-auth:
	@echo "Running authentication tests..."
	$(PYTHON) $(TEST_DIR)/test_user_auth.py

# Run integration test
.PHONY: test-integration
test-integration:
	@echo "Running integration tests..."
	$(PYTHON) $(TEST_DIR)/test_hello_integration.py

# Hello authenticated service tests removed (now covered by integration tests)

# Run the application
.PHONY: run
run:
	@echo "Starting the application..."
	$(PYTHON) run_app.py

# Clean up generated files
.PHONY: clean
clean:
	@echo "Cleaning up..."
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +

# Help command
.PHONY: help
help:
	@echo "FastAPI Starter Template Makefile"
	@echo ""
	@echo "Available commands:"
	@echo "  make                   Run all tests"
	@echo "  make install           Install dependencies"
	@echo "  make test              Run all tests (creates dev user in DB)"
	@echo "  make test-auth         Run authentication tests (creates dev user in DB)"
	@echo "  make test-integration  Run integration tests (creates dev user in DB)"
	@echo "  make run               Start the application"
	@echo "  make clean             Clean up generated files"
	@echo "  make help              Show this help message"
	@echo ""
	@echo "Note: Tests using authentication will automatically create a dev user in the database"
