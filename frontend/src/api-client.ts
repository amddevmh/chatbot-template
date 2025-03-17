import { useAuth } from './hooks/use-auth';
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { ChatSession, SessionHistoryResponse, SessionsListResponse, ChatResponse } from './types';

/**
 * API Client for making authenticated requests to the backend
 * 
 * This client automatically includes the authentication token in requests
 * and handles common response processing.
 */
class ApiClient {
  private baseUrl: string;
  private axiosInstance: AxiosInstance;
  
  constructor() {
    // Configure the base URL for API requests
    // Use environment variable if available, otherwise fall back to default
    this.baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
    
    // Create axios instance with default configuration
    this.axiosInstance = axios.create({
      baseURL: this.baseUrl,
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: true,
    });
  }
  
  /**
   * Make an authenticated GET request
   */
  async get<T>(endpoint: string, token?: string): Promise<T> {
    return this.request<T>('GET', endpoint, undefined, token);
  }
  
  /**
   * Make an authenticated POST request
   */
  async post<T>(endpoint: string, data?: any, token?: string): Promise<T> {
    return this.request<T>('POST', endpoint, data, token);
  }
  
  /**
   * Make an authenticated PUT request
   */
  async put<T>(endpoint: string, data?: any, token?: string): Promise<T> {
    return this.request<T>('PUT', endpoint, data, token);
  }
  
  /**
   * Make an authenticated DELETE request
   */
  async delete<T>(endpoint: string, token?: string): Promise<T> {
    return this.request<T>('DELETE', endpoint, undefined, token);
  }
  
  /**
   * Core request method that handles authentication and error processing
   */
  private async request<T>(
    method: string,
    endpoint: string,
    data?: any,
    token?: string
  ): Promise<T> {
    // Configure request options
    const config: AxiosRequestConfig = {
      method: method,
      url: endpoint,
    };
    
    // Add the authentication token if available
    if (token) {
      config.headers = {
        ...config.headers,
        'Authorization': `Bearer ${token}`
      };
    }
    
    // Add request body for POST and PUT requests
    if (data && (method === 'POST' || method === 'PUT')) {
      config.data = data;
    }
    
    try {
      // Make the request using axios
      const response = await this.axiosInstance.request<T>(config);
      
      // Return the response data
      return response.data;
    } catch (error) {
      // Handle axios errors
      if (axios.isAxiosError(error) && error.response) {
        const errorData = error.response.data;
        throw new Error(
          errorData.detail || `API error: ${error.response.status} ${error.response.statusText}`
        );
      }
      
      // Handle other errors
      throw error;
    }
  }
}

// Create and export a singleton instance
export const api = new ApiClient();

// Export type definitions for common API responses
export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: string;
}

/**
 * Chat API client for interacting with the backend chat service
 * 
 * This client handles authentication and provides methods for common chat operations.
 */
class ChatApiClient {
  private api: ApiClient;
  private auth: ReturnType<typeof useAuth> | null = null;
  
  constructor() {
    this.api = new ApiClient();
  }
  
  /**
   * Set the authentication context
   * This should be called from components that use the chat API
   */
  setAuth(auth: ReturnType<typeof useAuth>) {
    if (!auth) {
      console.warn('Attempted to set null auth context');
      return;
    }
    
    if (!auth.accessToken) {
      console.warn('Attempted to set auth context without access token');
      return;
    }
    
    this.auth = auth;
    console.log('Auth context set in ChatApiClient', !!auth.accessToken);
  }
  
  /**
   * Send a chat message to the backend
   */
  async sendMessage(message: string, sessionId?: string) {
    return this.api.post<ChatResponse>('/chat', {
      message,
      session_id: sessionId,
    }, this.auth?.accessToken || undefined);
  }
  
  /**
   * List all chat sessions for the current user
   */
  async listSessions() {
    if (!this.auth?.accessToken) {
      console.error('Attempted to list sessions without auth token');
      throw new Error('Authentication required');
    }
    
    console.log('Listing sessions with token', !!this.auth.accessToken);
    return this.api.get<SessionsListResponse>('/chat/sessions', this.auth.accessToken);
  }

  /**
   * Create a new chat session
   */
  async createSession(name: string = "New Chat") {
    if (!this.auth?.accessToken) {
      console.error('Attempted to create session without auth token');
      throw new Error('Authentication required');
    }
    
    console.log('Creating session with token', !!this.auth.accessToken);
    return this.api.post<ChatSession>('/chat/sessions', { name }, this.auth.accessToken);
  }
  
  /**
   * Get user profile information
   */
  async getUserProfile() {
    return this.api.get<any>('/me', this.auth?.accessToken || undefined);
  }
  
  /**
   * Get message history for a specific session
   */
  async getSessionHistory(sessionId: string) {
    if (!this.auth?.accessToken) {
      console.error('Attempted to get session history without auth token');
      throw new Error('Authentication required');
    }
    
    console.log('Getting session history with token', !!this.auth.accessToken);
    return this.api.get<SessionHistoryResponse>(
      `/chat/sessions/${sessionId}/history`, 
      this.auth.accessToken
    );
  }
  
  /**
   * Check API health
   */
  async checkHealth() {
    return this.api.get<{ status: string; message: string }>('/health');
  }
}

// Export a singleton instance of the chat API client
export const chatApi = new ChatApiClient();
