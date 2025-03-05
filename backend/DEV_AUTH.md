# Development Authentication

This document explains how to use the development authentication system for testing the API.

## Dev Token Authentication

For development and testing purposes, we've implemented a special authentication mechanism using a development token. This token is automatically mapped to a test user in the database.

### Generating a Dev Token

To generate a development token, run:

```bash
python generate_dev_token.py
```

This will output a token that you can use in your API requests.

### Using the Dev Token

Include the token in your API requests using the Authorization header:

```
Authorization: Bearer <your_dev_token>
```

### How It Works

1. When the system receives a token with the subject "dev_test_user", it recognizes it as a development token
2. The system checks if a user with username "dev_test_user" exists in the database
3. If the user doesn't exist, it automatically creates one with:
   - Username: dev_test_user
   - Email: dev@example.com
   - Password: devpassword123
   - Verified: true
   - Active: true
4. The request proceeds with this user's context

### Testing the Dev Token

You can test if the dev token is working correctly by running:

```bash
python test_user_auth.py
```

This script will:
1. Generate a dev token
2. Test authentication with the dev token

### Integration Testing with Dev Token

We've created several tests that use the dev token for authentication:

```bash
# Test the authentication mechanism with the dev token
python test_user_auth.py

# Test the message service directly
python test_message_service.py

# Full integration test (starts and stops its own server)
python test_message_integration.py
```

See the `TESTING.md` file for more details on our testing approach.

## Security Considerations

- The dev token is only intended for development and testing
- In production, all requests require proper authentication
- The dev token mechanism is not available in production mode
