import React, { createContext, useState, useEffect, useContext } from 'react';
import { getDevToken } from '../auth';
import { jwtDecode } from 'jwt-decode';

// Define the shape of our authentication context
interface AuthContextType {
  user: any | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  accessToken: string | null;
  signIn: () => Promise<void>;
  signOut: () => Promise<void>;
}

// Create the authentication context
const AuthContext = createContext<AuthContextType>({
  user: null,
  isAuthenticated: false,
  isLoading: true,
  accessToken: null,
  signIn: async () => {},
  signOut: async () => {},
});

/**
 * AuthProvider component provides authentication context throughout the application.
 * 
 * This is a simplified version of next-auth's SessionProvider that works with Vite.
 * It simulates the authentication flow using a hardcoded development token.
 */
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  
  // Initialize authentication state on component mount
  useEffect(() => {
    const initAuth = async () => {
      try {
        // In a real app, we would check for an existing session here
        // For development, we'll just use our hardcoded token
        const token = getDevToken();
        
        // Decode the token to get user information
        const decoded = jwtDecode<any>(token);
        
        setUser({
          id: decoded.sub || 'dev_test_user',
          name: 'Development User',
          email: 'dev@example.com',
          image: 'https://avatars.githubusercontent.com/u/1?v=4',
          token,
        });
        
        setAccessToken(token);
      } catch (error) {
        console.error('Error initializing auth:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    initAuth();
  }, []);
  
  // Sign in function (simulated for development)
  const signIn = async () => {
    setIsLoading(true);
    
    try {
      // In a real app, this would make an API request to authenticate
      // For development, we'll just use our hardcoded token
      const token = getDevToken();
      
      // Decode the token to get user information
      const decoded = jwtDecode<any>(token);
      
      setUser({
        id: decoded.sub || 'dev_test_user',
        name: 'Development User',
        email: 'dev@example.com',
        image: 'https://avatars.githubusercontent.com/u/1?v=4',
        token,
      });
      
      setAccessToken(token);
    } catch (error) {
      console.error('Error signing in:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Sign out function
  const signOut = async () => {
    setUser(null);
    setAccessToken(null);
  };
  
  // Provide the authentication context to children
  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        accessToken,
        signIn,
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
  return useContext(AuthContext);
}
