# Backend Authentication with Supabase

This template uses [Supabase](https://supabase.com) for authentication, with the backend verifying Supabase JWT tokens.

## Setup Instructions

### 1. Install Dependencies

The backend requires the Supabase Python client:

```bash
pip install supabase
```

Or update your requirements:

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Add the following to your `.env` file:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key
```

- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anon/public key (for client operations)
- `SUPABASE_SERVICE_KEY`: Your Supabase service role key (for admin operations)

### 3. Create a Development User

Run the setup script to create a development user:

```bash
python setup_dev_env.py
```

This will:
1. Create a user in Supabase with email `dev@example.com` and password `devpassword123`
2. Confirm the email automatically
3. Provide the credentials for development use

## Authentication Flow

1. The frontend authenticates with Supabase and receives a JWT token
2. The frontend includes this token in API requests to the backend
3. The backend verifies the token using the Supabase client
4. If valid, the user information is attached to the request state
5. API endpoints can access the authenticated user via the request state

## Implementation Details

### Middleware

The `verify_user_middleware` function in `middleware.py`:
1. Extracts the JWT token from the Authorization header
2. Verifies the token with Supabase
3. Creates an `AuthUser` object with the user information
4. Attaches the user to the request state

### Dependencies

The following dependencies are available for route handlers:

- `get_user_from_request`: Get the user from the request state
- `require_auth`: Require an authenticated user
- `require_role`: Require a specific role

### Example Usage

```python
from fastapi import APIRouter, Depends
from app.auth.middleware import require_auth
from app.auth.models import AuthUser

router = APIRouter()

@router.get("/me")
async def read_user_me(user: AuthUser = Depends(require_auth)):
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name
    }
```

## Customization

To customize the authentication flow or add additional providers, refer to the [Supabase Authentication documentation](https://supabase.com/docs/guides/auth).
