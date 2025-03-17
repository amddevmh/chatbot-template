/**
 * Shared type definitions for the chat application
 */

/**
 * Chat message type
 */
export interface ChatMessage {
  id: string;
  role: 'human' | 'ai';
  content: string;
  timestamp: string;
}

/**
 * Chat session type
 */
export interface ChatSession {
  session_id: string;
  name: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

/**
 * API response types
 */
export interface SessionHistoryResponse {
  messages: ChatMessage[];
}

export interface SessionsListResponse {
  sessions: ChatSession[];
}

export interface ChatResponse {
  response: string;
  session_id: string;
}
