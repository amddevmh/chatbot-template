import { AppSidebar } from "@/components/app-sidebar";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbList,
  BreadcrumbPage,
} from "@/components/ui/breadcrumb";
import { Separator } from "@/components/ui/separator";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { ThemeProvider } from "./components/theme-provider";
import { Button } from "./components/ui/button";
import { AuthProvider } from "./components/auth-provider";
import { useAuth } from "./hooks/use-auth";
import { useEffect, useState } from "react";
import { chatApi } from "./api-client";

// Component to display authentication status and user info
function AuthStatus() {
  const auth = useAuth();
  const { user, isAuthenticated, isLoading, signIn, signOut } = auth;
  const [apiHealth, setApiHealth] = useState<string>("Checking...");
  
  // Initialize the chat API with authentication
  useEffect(() => {
    // Set the auth context in the chat API
    chatApi.setAuth(auth);
  }, [auth]);
  
  // Check API health on component mount
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const health = await chatApi.checkHealth();
        setApiHealth(`API Status: ${health.status}`);
      } catch (error) {
        setApiHealth("API Status: Error connecting to backend");
        console.error("API Health check failed:", error);
      }
    };
    
    checkHealth();
  }, []);
  
  if (isLoading) {
    return <div>Loading authentication status...</div>;
  }
  
  return (
    <div className="space-y-4 p-4 bg-muted/50 rounded-lg">
      <h2 className="text-xl font-bold">Authentication Status</h2>
      <div className="space-y-2">
        <p>Status: {isAuthenticated ? "Authenticated" : "Not authenticated"}</p>
        <p>API: {apiHealth}</p>
        {isAuthenticated && user && (
          <div className="space-y-1">
            <p>User: {user.name}</p>
            <p>Email: {user.email}</p>
            <p className="text-xs text-muted-foreground break-all">
              Token: {user.token ? user.token.substring(0, 20) + "..." : "None"}
            </p>
          </div>
        )}
        <div className="flex gap-2 pt-2">
          {!isAuthenticated ? (
            <Button onClick={() => signIn()}>Sign In</Button>
          ) : (
            <Button variant="outline" onClick={() => signOut()}>Sign Out</Button>
          )}
        </div>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
        <SidebarProvider>
          <AppSidebar />
          <SidebarInset>
            <header className="sticky top-0 flex h-16 shrink-0 items-center gap-2 border-b bg-background px-4">
              <SidebarTrigger className="-ml-1" />
              <Separator orientation="vertical" className="mr-2 h-4" />
              <Breadcrumb>
                <BreadcrumbList>
                  <BreadcrumbItem>
                    <BreadcrumbPage>Chatbot Template</BreadcrumbPage>
                  </BreadcrumbItem>
                </BreadcrumbList>
              </Breadcrumb>
            </header>
            <div className="flex flex-1 flex-col gap-4 p-4">
              <AuthStatus />
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 border rounded-lg">
                  <h2 className="text-lg font-medium mb-2">Backend Integration</h2>
                  <p className="text-muted-foreground mb-4">
                    The frontend is now connected to your FastAPI backend using Auth.js for authentication.
                    The development token is automatically included in all API requests.
                  </p>
                  <Button onClick={async () => {
                    try {
                      const response = await chatApi.sendMessage("Hello from the frontend!");
                      alert(`Backend response: ${response.response}`);
                    } catch (error) {
                      alert(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
                    }
                  }}>
                    Test Chat API
                  </Button>
                </div>
              </div>
            </div>
          </SidebarInset>
        </SidebarProvider>
      </ThemeProvider>
    </AuthProvider>
  );
}
