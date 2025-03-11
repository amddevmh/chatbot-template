# FastAPI Starter Template Makefile
# This Makefile provides commands for running tests and other common tasks

# Variables
PYTHON = python3
TEST_DIR = tests
VENV_DIR = venv
VENV_ACTIVATE = . $(VENV_DIR)/bin/activate

# Default target
.PHONY: all
all: test

# Setup the project
.PHONY: setup
setup:
	@echo "Running setup script..."
	./setup.sh

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


# Run the application
.PHONY: run
run:
	@echo "Starting the application..."
	$(PYTHON) run_app.py

# Generate a development token
.PHONY: token
token:
	@echo "Generating development token..."
	$(VENV_ACTIVATE) && $(PYTHON) generate_dev_token.py

# Help command
.PHONY: help
help:
	@echo "FastAPI Starter Template Makefile"
	@echo ""
	@echo "Available commands:"
	@echo "  make                   Run all tests"
	@echo "  make setup             Complete project setup (creates venv, installs deps, copies env file)"
	@echo "  make install           Install dependencies"
	@echo "  make test              Run all tests (creates dev user in DB)"
	@echo "  make test-auth         Run authentication tests (creates dev user in DB)"
	@echo "  make test-integration  Run integration tests (creates dev user in DB)"
	@echo "  make run               Start the application"
	@echo "  make token             Generate a development token for testing"
	@echo ""
	@echo "Note: Tests using authentication will automatically create a dev user in the database"
