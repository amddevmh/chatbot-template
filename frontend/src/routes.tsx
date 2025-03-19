import { createBrowserRouter } from 'react-router-dom';
import App from './App';
import { ChatView } from './components/chat-view';
import { NotFound } from './components/not-found';

// Define the base path for the application
// This should match the base path in your vite.config.ts
const basePath = '/react-starter';

// Create and export the router configuration
export const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      {
        index: true,
        element: <ChatView />,
      },
      {
        path: '*',
        element: <NotFound />,
      },
    ],
  },
], {
  basename: basePath,
});
