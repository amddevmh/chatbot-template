import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from "path"

// https://vite.dev/config/
export default defineConfig({
  base: '/',
  server:{
    port: 3000,
  },
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  // Define global variables for the browser environment
  define: {
    // Polyfill for process.env used by next-auth
    'process.env': {
      NODE_ENV: JSON.stringify(process.env.NODE_ENV || 'development'),
      NEXTAUTH_URL: JSON.stringify('http://localhost:3000'),
      // API URL - default to localhost for development, but can be overridden
      VITE_API_URL: JSON.stringify(process.env.VITE_API_URL || 'http://localhost:8000/api/v1'),
      // Add any other environment variables needed by next-auth here
    },
  },
})
