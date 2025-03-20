import { createBrowserRouter, Navigate, useRouteError, isRouteErrorResponse, Link, Outlet } from "react-router-dom";

console.log('Router module is being executed');
import { useAuth } from "./hooks/use-auth";
import App from "./App";
import { ChatView } from "./components/chat-view";
import { LoginPage } from "./components/login-page";

// Protected route wrapper that redirects to login if not authenticated
function ProtectedRoute() {
  console.log('ProtectedRoute component is being rendered');
  const auth = useAuth();
  console.log('Auth state in ProtectedRoute:', {
    isAuthenticated: auth.isAuthenticated,
    isLoading: auth.isLoading,
    hasUser: !!auth.user,
    hasSession: !!auth.session,
    hasToken: !!auth.accessToken
  });
  
  // Show nothing while checking authentication
  if (auth.isLoading) {
    console.log('Auth is still loading, showing loading screen');
    return <div className="flex h-screen items-center justify-center">Loading...</div>;
  }
  
  // Redirect to login if not authenticated
  if (!auth.isAuthenticated) {
    console.log('User is not authenticated, redirecting to login');
    return <Navigate to="/login" replace />;
  }
  
  // Render child routes if authenticated
  console.log('User is authenticated, rendering child routes');
  return <Outlet />;
}

// Enhanced error page component that shows different messages based on error type
function ErrorPage() {
  const error = useRouteError();
  let errorMessage = "An unexpected error has occurred.";
  let errorTitle = "Something went wrong";
  
  if (isRouteErrorResponse(error)) {
    if (error.status === 404) {
      errorTitle = "Page not found";
      errorMessage = "The page you're looking for doesn't exist or has been moved.";
    } else {
      errorMessage = error.statusText || errorMessage;
    }
  } else if (error instanceof Error) {
    errorMessage = error.message;
  }
  
  return (
    <div className="flex h-screen w-screen items-center justify-center p-8 text-center">
      <div className="max-w-md space-y-4">
        <h3 className="text-xl font-semibold">{errorTitle}</h3>
        <p className="text-muted-foreground">{errorMessage}</p>
        <Link to="/" className="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2">
          Go back home
        </Link>
      </div>
    </div>
  );
}

// Wrapper component for LoginPage to log when it's rendered
function LoginPageWrapper() {
  console.log('LoginPageWrapper component is being rendered');
  return <LoginPage />;
}

export const router = createBrowserRouter([
  {
    path: "/login",
    element: <LoginPageWrapper />,
    errorElement: <ErrorPage />,
  },
  {
    path: "/",
    element: <ProtectedRoute />,
    errorElement: <ErrorPage />,
    children: [
      {
        element: <App />,
        children: [
          {
            index: true,
            element: <Navigate to="/chat" replace />,
          },
          {
            path: "chat",
            element: <ChatView />
          },
          {
            path: "chat/:sessionId",
            element: <ChatView />
          }
        ]
      }
    ]
  }
]);
