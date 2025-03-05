# Testing Documentation

## Overview

This document describes the testing approach for the Nutrition Assistant API, focusing on authentication mechanisms and message processing.

## Test Types

### 1. Authentication Tests

#### Dev Token Authentication (`test_user_auth.py`)

This test verifies the development token authentication mechanism:

- Initializes the database connection
- Generates a development token
- Authenticates using the token
- Verifies that the dev_test_user is properly created and authenticated

The dev token is a special JWT token that automatically creates/retrieves a test user account, making integration testing much simpler.

### 2. Integration Tests

#### Message Processing (`test_message_integration.py`)

This test verifies the end-to-end flow of message processing with authentication:

- Initializes the database with required models
- Starts the API server
- Generates a development token
- Sends a message to the API endpoint
- Verifies the response contains the expected greeting
- Stops the API server

This test ensures that:
1. The authentication middleware correctly identifies the dev token
2. The message processing endpoint works correctly
3. The personalized greeting is included in the response

### 3. Direct Service Tests

#### Message Service (`test_message_service.py`)

This test directly tests the message service without going through the API:

- Creates a message service instance
- Sends a test message
- Verifies the response contains the expected greeting

This test focuses on the business logic of the message service without the overhead of HTTP and authentication.



## Running Tests

### Using the Makefile

The easiest way to run tests is using the provided Makefile:

```bash
# Run all tests
make test

# Run specific test categories
make test-auth            # Run authentication tests
make test-message-service # Run message service tests
make test-integration     # Run integration tests

# See all available commands
make help
```

### Running Tests Directly

You can also run the tests directly using Python:

```bash
# Authentication test
python test_user_auth.py

# Message service test
python test_message_service.py

# Integration test (starts and stops its own server)
python test_message_integration.py
```

## Test Environment

The tests currently use the real database configured in the application settings. For more robust testing, consider:

1. Using a separate test database
2. Implementing database mocking for unit tests
3. Adding cleanup code to remove test data after tests complete
