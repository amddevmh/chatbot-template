import { useAuth } from './hooks/use-auth';
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';

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
    // In development, this points to the local backend
    // In production, this would be configured based on environment
    this.baseUrl = 'http://localhost:8000/api/v1';
    
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
    this.auth = auth;
  }
  
  /**
   * Send a chat message to the backend
   */
  async sendMessage(message: string, sessionId?: string) {
    return this.api.post<{ response: string }>('/chat', {
      message,
      session_id: sessionId,
    }, this.auth?.accessToken || undefined);
  }
  
  /**
   * Get user profile information
   */
  async getUserProfile() {
    return this.api.get<any>('/me', this.auth?.accessToken || undefined);
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
