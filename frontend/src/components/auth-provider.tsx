import React, { createContext, useState, useEffect, useContext } from 'react';
import { supabase } from '../lib/supabase-client';
import type { User, Session } from '@supabase/supabase-js';

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
    }, 3000);
    
    return () => clearTimeout(timeoutId);
  }, [isLoading]);

  // Initialize authentication state on component mount
  useEffect(() => {
    let isMounted = true; // Flag to prevent state updates after unmount

    const initAuth = async () => {
      try {
        // Get the current session
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
          if (isMounted) setIsLoading(false);
        }
      } catch (error) {
        console.error('Error initializing auth:', error);
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
  const authContext = useContext(AuthContext);
  return authContext;
}
