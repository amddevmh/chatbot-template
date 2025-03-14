import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

// Initialize the application
async function initApp() {
  // This is where we would initialize Auth.js in a Next.js application
  // For our Vite app, the initialization happens in the AuthProvider component
  
  // Render the application
  createRoot(document.getElementById('root')!).render(
    <StrictMode>
      <App />
    </StrictMode>,
  )
}

// Start the application
initApp().catch(console.error)
