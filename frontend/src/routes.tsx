import { createBrowserRouter } from 'react-router-dom';
import App from './App';
import ChatView from './views/ChatView';
import ChatList from './views/ChatList';
import NotFound from './views/NotFound';

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
        element: <ChatList />,
      },
      {
        path: 'chat/:chatId',
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
