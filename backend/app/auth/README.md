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

### Authentication Dependencies

The authentication system uses FastAPI dependencies for route protection:

- `get_current_user`: Extracts and validates the JWT token from the Authorization header, returning an AuthUser object
- `require_auth`: Ensures a user is authenticated, raising an HTTPException if not
- `require_role`: Requires a specific role for the authenticated user

### Example Usage

```python
from fastapi import APIRouter, Depends
from app.auth.security import get_current_user
from app.auth.models import AuthUser

router = APIRouter()

@router.get("/me")
async def read_user_me(current_user: AuthUser = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name
    }
```

## Customization

To customize the authentication flow or add additional providers, refer to the [Supabase Authentication documentation](https://supabase.com/docs/guides/auth).
