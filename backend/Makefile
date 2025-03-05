# Nutrition Assistant API Makefile
# This Makefile provides commands for running tests and other common tasks

# Variables
PYTHON = python
TEST_DIR = .
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
	@echo "\n=== Message Service Tests ===\n"
	$(MAKE) test-message-service
	@echo "\n=== Integration Tests ===\n"
	$(MAKE) test-integration
	@echo "\n=== All tests completed successfully! ===\n"

# Run authentication test
.PHONY: test-auth
test-auth:
	@echo "Running authentication tests..."
	$(PYTHON) $(TEST_DIR)/test_user_auth.py

# Run message service test
.PHONY: test-message-service
test-message-service:
	@echo "Running message service tests..."
	$(PYTHON) $(TEST_DIR)/test_message_service.py

# Run integration test
.PHONY: test-integration
test-integration:
	@echo "Running integration tests..."
	$(PYTHON) $(TEST_DIR)/test_message_integration.py

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
	@echo "Nutrition Assistant API Makefile"
	@echo ""
	@echo "Available commands:"
	@echo "  make                   Run all tests"
	@echo "  make install           Install dependencies"
	@echo "  make test              Run all tests"
	@echo "  make test-auth         Run authentication tests"
	@echo "  make test-message-service  Run message service tests"
	@echo "  make test-integration  Run integration tests"
	@echo "  make run               Start the application"
	@echo "  make clean             Clean up generated files"
	@echo "  make help              Show this help message"
