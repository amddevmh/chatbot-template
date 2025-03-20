import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/hooks/use-auth";
import { Github, Chrome, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export function LoginPage() {
  console.log("LoginPage component is being rendered");
  const { signIn, signInWithPassword, isAuthenticated } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isDev, setIsDev] = useState(false);
  const navigate = useNavigate();

  // Handle dev credentials
  React.useEffect(() => {
    const devEmail = import.meta.env.VITE_SUPABASE_DEV_EMAIL;
    const devPassword = import.meta.env.VITE_SUPABASE_DEV_PASSWORD;
    if (import.meta.env.DEV && !!devEmail && !!devPassword) {
      setIsDev(true);
    }
  }, []);

  // Redirect if already authenticated
  React.useEffect(() => {
    if (isAuthenticated) {
      navigate("/");
    }
  }, [isAuthenticated, navigate]);

  // Handle email/password sign in
  const handleEmailSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      await signInWithPassword(email, password);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to sign in");
    } finally {
      setIsLoading(false);
    }
  };

  //Handle Dev Login
  const handleDevLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    const devEmail = import.meta.env.VITE_SUPABASE_DEV_EMAIL;
    const devPassword = import.meta.env.VITE_SUPABASE_DEV_PASSWORD;

    if (!devEmail || !devPassword) {
      setError("Development credentials not found");
      return;
    }

    try {
      await signInWithPassword(devEmail, devPassword);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to sign in");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <div className="w-full max-w-md space-y-8 rounded-lg border bg-card p-6 shadow-sm">
        <div className="space-y-2 text-center">
          <h1 className="text-3xl font-bold">Sign In</h1>
          <p className="text-muted-foreground">
            Choose your preferred sign in method
          </p>
        </div>

        <div className="space-y-4">
          {isDev && (
            <Button
              variant="outline"
              className="w-full flex items-center justify-center gap-2"
              onClick={handleDevLogin}
              disabled={isLoading}
            >
              <User size={16} />
              Sign in with Dev
            </Button>
          )}

          <Button
            variant="outline"
            className="w-full flex items-center justify-center gap-2"
            onClick={() => signIn("github")}
            disabled={isLoading}
          >
            <Github size={16} />
            Sign in with GitHub
          </Button>

          <Button
            variant="outline"
            className="w-full flex items-center justify-center gap-2"
            onClick={() => signIn("google")}
            disabled={isLoading}
          >
            <Chrome size={16} />
            Sign in with Google
          </Button>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-card px-2 text-muted-foreground">
                Or continue with
              </span>
            </div>
          </div>

          <form onSubmit={handleEmailSignIn} className="space-y-4">
            {error && (
              <div className="rounded bg-destructive/10 p-3 text-sm text-destructive">
                {error}
              </div>
            )}

            <div className="space-y-2">
              <Input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={isLoading}
                required
              />
            </div>

            <div className="space-y-2">
              <Input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={isLoading}
                required
              />
            </div>

            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? "Signing in..." : "Sign In with Email"}
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}
