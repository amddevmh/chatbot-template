# FastAPI Starter Template

A production-ready FastAPI starter template with MongoDB integration, JWT authentication, comprehensive testing infrastructure, and environment configuration.

## Quick Start

```bash
# Clone the repository
git clone https://github.com/amddevmh/fast-api-starter.git
cd fast-api-starter

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Run the application
make run
```

Visit http://localhost:8000/docs to see the API documentation.

## Development

For development, the template includes a convenient dev token system that automatically creates a test user in the database when used.

See [DEVELOPMENT.md](docs/DEVELOPMENT.md) for details on authentication, testing, and development workflow.

## API Endpoints

- `GET /health` - Health check endpoint
- `GET /api/v1/auth/me` - Get current user information
- `GET /api/v1/hello_authenticated` - Get a personalized greeting (requires authentication)
- `POST /api/examples/process` - Process example requests

## Project Structure

This template follows a modular and organized structure to promote maintainability and scalability.

For a detailed overview of the project structure, see [PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md).

## Testing

Run the tests with:

```bash
make test
```

See [DEVELOPMENT.md](docs/DEVELOPMENT.md) for more details on testing.

## License

MIT
