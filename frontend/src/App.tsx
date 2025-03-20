// App.tsx - Main application container
import React from "react";
import { Outlet } from "react-router-dom";
import { ThemeProvider } from "./components/theme-provider";
import { AuthProvider } from "./components/auth-provider";

export default function App() {
  console.log('App component is being rendered');
  
  // Log when the component is mounted
  React.useEffect(() => {
    console.log('App component mounted');
    return () => {
      console.log('App component unmounted');
    };
  }, []);
  return (
    <AuthProvider>
      <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
        <Outlet />
      </ThemeProvider>
    </AuthProvider>
  );
}
