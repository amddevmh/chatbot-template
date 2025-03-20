# Supabase Authentication Setup

This template uses [Supabase](https://supabase.com) for authentication, including social login providers like GitHub and Google.

## Setup Instructions

### 1. Create a Supabase Project

1. Go to [Supabase](https://supabase.com) and sign up or log in
2. Create a new project
3. Note your project URL and anon key (found in Project Settings > API)

### 2. Configure Environment Variables

Add the following to your `.env.local` file:

```
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_KEY=your-anon-key
```

For development, you can also add:

```
VITE_SUPABASE_DEV_EMAIL=dev@example.com
VITE_SUPABASE_DEV_PASSWORD=devpassword123
```

### 3. Set Up Social Providers

#### GitHub

1. Go to your GitHub account settings
2. Navigate to Developer Settings > OAuth Apps > New OAuth App
3. Set the Authorization callback URL to: `https://your-project.supabase.co/auth/v1/callback`
4. Copy the Client ID and Client Secret
5. In Supabase dashboard, go to Authentication > Providers > GitHub
6. Enable GitHub and paste your Client ID and Client Secret
7. Save changes

#### Google

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to APIs & Services > Credentials
4. Create an OAuth 2.0 Client ID
5. Add `https://your-project.supabase.co/auth/v1/callback` as an authorized redirect URI
6. Copy the Client ID and Client Secret
7. In Supabase dashboard, go to Authentication > Providers > Google
8. Enable Google and paste your Client ID and Client Secret
9. Save changes

### 4. Set Up Backend Integration

1. Add the following to your backend `.env` file:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key
```

2. Run the setup script to create a development user:

```bash
cd backend
python setup_dev_env.py
```

## Usage

### Authentication Flow

The authentication flow is handled by the `AuthProvider` component, which:

1. Checks for an existing session on load
2. Provides methods for signing in with social providers or email/password
3. Manages the user state and access token

### Protected Routes

Routes that require authentication are wrapped with the `ProtectedRoute` component, which redirects to the login page if the user is not authenticated.

### API Integration

The API client automatically includes the Supabase access token in requests to the backend, which verifies the token and gets the user information.

## Development Mode

In development mode, the application will automatically sign in with the development user if the environment variables `VITE_SUPABASE_DEV_EMAIL` and `VITE_SUPABASE_DEV_PASSWORD` are set.

## Customization

To add more social providers or customize the authentication flow, refer to the [Supabase Authentication documentation](https://supabase.com/docs/guides/auth).
