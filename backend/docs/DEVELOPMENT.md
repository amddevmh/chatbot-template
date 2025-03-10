# Development Guide

This guide covers development practices, testing, and authentication for the FastAPI Starter Template.

## Authentication

### Development Token

For development and testing, use the built-in dev token system:

```bash
# Generate a development token
python generate_dev_token.py
```

This creates a token for the `dev_test_user` account that you can use in API requests. **Important**: When you use this token, the system will automatically create a dev user in the database if it doesn't already exist:

- Username: `dev_test_user`
- Email: `dev@example.com`
- Verified: `true`
- Active: `true`

To use the token in your API requests:

```bash
# Use the token in your requests
curl -X GET "http://localhost:8000/api/v1/hello_authenticated" \
  -H "Authorization: Bearer <your_token>"
```

## Testing

### Running Tests

```bash
# Run all tests
make test

# Run specific test categories
make test-auth            # Authentication tests
make test-integration     # Integration tests
```

### Test Types

1. **Authentication Tests** (`tests/test_user_auth.py`)
   - Verifies dev token authentication works correctly

2. **Integration Tests** (`tests/test_hello_integration.py`)
   - Tests the hello_authenticated service with authentication
   - Starts a FastAPI server in a separate process
   - Tests the GET endpoint

## Development Workflow

1. Start the server: `make run`
2. Generate a dev token: `python generate_dev_token.py`
3. Test your endpoints using the token
4. Run tests to verify your changes: `make test`

## Testing with curl

You can test the API endpoints using curl commands. First, generate a development token:

```bash
python -c "from app.auth.security import create_dev_token; print(create_dev_token())"
```

This will output a JWT token that you can use in your requests. Here are some example curl commands for testing the main endpoints:

### Hello Authenticated Endpoint

```bash
curl -X GET "http://localhost:8000/api/v1/hello_authenticated" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZXZfdGVzdF91c2VyIn0.AkJIxSVHaJkCRB653MH0ZgTw00DEczPLOA-MaqUQXgc" \
  -H "Content-Type: application/json" | jq
```

### Chat Endpoint

#### Send a message to the chat service:

```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZXZfdGVzdF91c2VyIn0.AkJIxSVHaJkCRB653MH0ZgTw00DEczPLOA-MaqUQXgc" \
  -H "Content-Type: application/json" \
  -d '{"message": "My name is John", "session_id": "test-session-1"}' | jq
```

#### Continue the conversation with the same session ID:

```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZXZfdGVzdF91c2VyIn0.AkJIxSVHaJkCRB653MH0ZgTw00DEczPLOA-MaqUQXgc" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is my name?", "session_id": "test-session-1"}' | jq
```

### Testing with Docker

If you're running the application in Docker using docker-compose, the curl commands remain the same, but make sure the server is accessible at http://localhost:8000.

```bash
# Start the Docker containers
docker-compose up -d

# Run the same curl commands as above

# Stop the Docker containers when done
docker-compose down
```

## Project Structure

See [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) for details on the codebase organization.
