import { createBrowserRouter, Navigate, useRouteError, isRouteErrorResponse, Link } from "react-router-dom";
import App from "./App";
import { ChatView } from "./components/chat-view";

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

export const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    errorElement: <ErrorPage />,
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
]);
