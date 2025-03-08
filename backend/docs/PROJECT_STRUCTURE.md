# Project Structure

This FastAPI starter template follows a modular and organized structure to promote maintainability and scalability.

## Directory Structure

```
fast-api-starter/
├── app/                      # Main application package
│   ├── api/                  # API routes and endpoints
│   │   ├── __init__.py
│   │   └── routes.py         # API route definitions
│   ├── auth/                 # Authentication components
│   │   ├── __init__.py
│   │   ├── middleware.py     # Auth middleware
│   │   ├── routes.py         # Auth endpoints
│   │   └── security.py       # JWT and security utilities
│   ├── database/             # Database connection and utilities
│   │   ├── __init__.py
│   │   └── mongodb.py        # MongoDB connection
│   ├── models/               # Data models
│   │   ├── __init__.py
│   │   ├── example.py        # Example models
│   │   ├── hello.py          # Hello authenticated models
│   │   └── user.py           # User models
│   ├── services/             # Business logic services
│   │   ├── __init__.py
│   │   ├── example_service.py # Example service
│   │   ├── hello_service.py  # Hello authenticated service
│   │   └── user_service.py   # User management service
│   ├── __init__.py
│   ├── application.py        # FastAPI application setup
│   ├── config.py             # Configuration settings
│   └── main.py               # Application entry point
├── docs/                     # Documentation files
│   ├── DEVELOPMENT.md        # Development documentation
│   └── PROJECT_STRUCTURE.md  # Project structure documentation
├── tests/                    # Test files
│   ├── __init__.py
│   ├── test_user_auth.py     # Authentication tests
│   └── test_hello_integration.py # Hello authenticated integration tests
├── .gitignore                # Git ignore file
├── Makefile                  # Makefile for common commands
├── README.md                 # Project documentation
├── requirements.txt          # Python dependencies
├── run_app.py                # Script to run the application
└── generate_dev_token.py     # Utility to generate dev tokens
```

## Key Components

- **API Layer**: Routes and endpoints for the application
- **Authentication**: JWT-based authentication with development token support
- **Database**: MongoDB connection using Beanie ODM
- **Models**: Pydantic models for data validation
- **Services**: Business logic implementation

## Design Principles

1. **Separation of Concerns**: Each module has a specific responsibility
2. **Dependency Injection**: Services and dependencies are injected where needed
3. **Testability**: Code is structured to be easily testable
4. **Security**: Authentication and authorization built-in
