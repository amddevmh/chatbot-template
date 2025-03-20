import React, { createContext, useState, useEffect, useContext } from 'react';
import { supabase } from '../lib/supabase-client';
import type { User, Session } from '@supabase/supabase-js';

// Define the shape of our authentication context
interface AuthContextType {
  user: User | null;
  session: Session | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  accessToken: string | null;
  signIn: (provider?: 'github' | 'google' | 'facebook') => Promise<void>;
  signInWithPassword: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
}

// Create the authentication context
const AuthContext = createContext<AuthContextType>({
  user: null,
  session: null,
  isAuthenticated: false,
  isLoading: true,
  accessToken: null,
  signIn: async () => {},
  signInWithPassword: async () => {},
  signOut: async () => {},
});

/**
 * AuthProvider component provides authentication context throughout the application.
 * 
 * This uses Supabase Auth for authentication, including social providers.
 */
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  
  // Add a timeout to ensure isLoading is set to false after a certain amount of time
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (isLoading) {
        console.log('Auth initialization timeout reached, forcing isLoading to false');
        setIsLoading(false);
      }
    }, 3000); // Reduced to 3 seconds timeout
    
    return () => clearTimeout(timeoutId);
  }, [isLoading]);

  // Initialize authentication state on component mount
  useEffect(() => {
    console.log('initAuth effect triggered');
    let isMounted = true; // Flag to prevent state updates after unmount

    const initAuth = async () => {
      console.log('initAuth function execution started');
      try {
        // Get the current session
        console.log('Getting current session from Supabase');
        const { data: { session }, error: sessionError } = await supabase.auth.getSession();
        
        if (sessionError) {
          console.error('Error getting session:', sessionError.message);
          if (isMounted) setIsLoading(false);
          return;
        }
        
        console.log('Session from Supabase:', !!session);
        
        if (session) {
          console.log('Session found, setting session and user');
          if (isMounted) {
            setSession(session);
            setUser(session.user);
            setIsLoading(false);
          }
        } else {
          console.log('No session found, checking for dev credentials');
          const USE_DEV_USER = true;
          // Auto-login in development mode if credentials are provided
          if (import.meta.env.DEV && USE_DEV_USER) {
            const devEmail = import.meta.env.VITE_SUPABASE_DEV_EMAIL;
            const devPassword = import.meta.env.VITE_SUPABASE_DEV_PASSWORD;
            
            console.log('Dev credentials available:', { 
              hasEmail: !!devEmail, 
              hasPassword: !!devPassword,
              email: devEmail
            });
            
            if (devEmail && devPassword) {
              console.log('Development mode: Auto-login with dev credentials');
              try {
                console.log('Attempting to sign in with dev credentials');
                const { data, error } = await supabase.auth.signInWithPassword({
                  email: devEmail,
                  password: devPassword,
                });
                
                if (error) {
                  console.error('Dev auto-login failed:', error.message);
                } else if (data.session) {
                  console.log('Dev auto-login successful');
                  console.log('Session token available:', !!data.session.access_token);
                  if (isMounted) {
                    setSession(data.session);
                    setUser(data.user);
                  }
                } else {
                  console.log('No error but no session returned');
                }
              } catch (e) {
                console.error('Error during dev auto-login:', e);
              }
            } else {
              console.log('Dev credentials not available, skipping auto-login');
            }
          }
          
          // Always set loading to false after attempting auto-login
          if (isMounted) setIsLoading(false);
        }
      } catch (error) {
        console.error('Error initializing auth:', error);
        // Make sure to set loading to false if there's an error
        if (isMounted) setIsLoading(false);
      }
    };
    
    // Set up auth state listener
    console.log('Setting up auth state change listener');
    let subscription: { unsubscribe: () => void } | null = null;
    
    try {
      const { data } = supabase.auth.onAuthStateChange((event, session) => {
        console.log('Auth state changed:', { event, hasSession: !!session });
        if (isMounted) {
          setSession(session);
          setUser(session?.user ?? null);
          setIsLoading(false);
        }
        console.log('Auth state updated, isLoading set to false');
      });
      
      subscription = data.subscription;
      console.log('Auth state change listener set up successfully');
    } catch (error) {
      console.error('Error setting up auth state listener:', error);
      if (isMounted) setIsLoading(false);
    }
    
    // Initialize auth
    initAuth();
    
    // Clean up on unmount
    return () => {
      console.log('Cleaning up auth provider');
      isMounted = false;
      if (subscription) {
        console.log('Unsubscribing from auth state changes');
        subscription.unsubscribe();
      }
    };
  }, []);
  
  // Sign in with social provider
  const signIn = async (provider?: 'github' | 'google' | 'facebook') => {
    setIsLoading(true);
    
    try {
      if (provider) {
        // Sign in with OAuth provider
        const { error } = await supabase.auth.signInWithOAuth({
          provider,
          options: {
            redirectTo: window.location.origin,
          },
        });
        
        if (error) {
          console.error('Error signing in with OAuth:', error.message);
        }
      } else {
        // If no provider specified, show sign-in UI or use default provider
        const { error } = await supabase.auth.signInWithOAuth({
          provider: 'github',
          options: {
            redirectTo: window.location.origin,
          },
        });
        
        if (error) {
          console.error('Error signing in with default provider:', error.message);
        }
      }
    } catch (error) {
      console.error('Error signing in:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Sign in with email and password
  const signInWithPassword = async (email: string, password: string) => {
    setIsLoading(true);
    
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });
      
      if (error) {
        console.error('Error signing in with password:', error.message);
      } else if (data.session) {
        console.log('Sign in successful, session established');
      } else {
        console.log('Sign in response received but no session data');
      }
    } catch (error) {
      console.error('Error signing in with password:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Sign out
  const signOut = async () => {
    try {
      const { error } = await supabase.auth.signOut();
      
      if (error) {
        console.error('Error signing out:', error.message);
      }
    } catch (error) {
      console.error('Error signing out:', error);
    }
  };
  
  // Provide the authentication context to children
  return (
    <AuthContext.Provider
      value={{
        user,
        session,
        isAuthenticated: !!user,
        isLoading,
        accessToken: session?.access_token ?? null,
        signIn,
        signInWithPassword,
        signOut,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

/**
 * Custom hook for accessing authentication context
 */
export function useAuth() {
  console.log('useAuth hook called');
  const authContext = useContext(AuthContext);
  console.log('Auth context in useAuth hook:', {
    isAuthenticated: authContext.isAuthenticated,
    isLoading: authContext.isLoading,
    hasUser: !!authContext.user,
    hasSession: !!authContext.session,
    hasToken: !!authContext.accessToken
  });
  return authContext;
}
