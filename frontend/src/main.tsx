import React, { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { RouterProvider } from 'react-router-dom'
import './index.css'
import { router } from './router'
import { AuthProvider } from './components/auth-provider'

console.log('Environment variables check:', {
  apiUrl: import.meta.env.VITE_API_URL,
  supabaseUrl: import.meta.env.VITE_SUPABASE_URL,
  supabaseKeyExists: !!import.meta.env.VITE_SUPABASE_KEY,
  devEmailExists: !!import.meta.env.VITE_SUPABASE_DEV_EMAIL,
  devPasswordExists: !!import.meta.env.VITE_SUPABASE_DEV_PASSWORD
});

// Create a client with improved configuration
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      refetchOnWindowFocus: false,
      retry: 2, // Retry failed queries twice
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000), // Exponential backoff
    },
    mutations: {
      retry: 1, // Retry failed mutations once
      retryDelay: 1000, // 1 second delay before retry
    },
  },
})

// Initialize the application
async function initApp() {
  console.log('initApp function called');
  
  // Create a wrapper component to log when the router is mounted
  const RouterWrapper = () => {
    console.log('RouterWrapper component rendering');
    
    React.useEffect(() => {
      console.log('RouterWrapper component mounted');
      return () => {
        console.log('RouterWrapper component unmounted');
      };
    }, []);
    
    // Wrap RouterProvider with AuthProvider to provide authentication context
    return (
      <AuthProvider>
        <RouterProvider router={router} />
      </AuthProvider>
    );
  };
  
  // Render the application
  createRoot(document.getElementById('root')!).render(
    <StrictMode>
      <QueryClientProvider client={queryClient}>
        <RouterWrapper />
      </QueryClientProvider>
    </StrictMode>,
  )
}

// Start the application
initApp().catch(console.error)
