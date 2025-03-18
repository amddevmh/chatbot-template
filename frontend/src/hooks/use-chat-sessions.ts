import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { chatApi } from "@/api-client"
import { useAuth } from "@/hooks/use-auth"
import { useEffect } from "react"
import { ChatSession, SessionsListResponse } from "@/types"

/**
 * Custom hook for managing chat sessions with TanStack Query
 */
export function useChatSessions() {
  const auth = useAuth()
  const queryClient = useQueryClient()
  
  // Ensure chatApi has the latest auth context
  useEffect(() => {
    if (auth && auth.accessToken) {
      chatApi.setAuth(auth)
      console.log("Auth set in useChatSessions hook", auth.isAuthenticated, !!auth.accessToken)
    }
  }, [auth, auth.isAuthenticated, auth.accessToken])
  
  // Query for fetching sessions
  const sessionsQuery = useQuery<SessionsListResponse>({
    queryKey: ["chatSessions", auth.isAuthenticated, auth.accessToken],
    queryFn: async () => {
      if (!auth.isAuthenticated || !auth.accessToken) {
        return { sessions: [] }
      }
      // Ensure auth is set before making the request
      chatApi.setAuth(auth)
      return await chatApi.listSessions()
    },
    // Only fetch if the user is authenticated and has a token
    enabled: auth.isAuthenticated && !!auth.accessToken,
    // Retry failed queries
    retry: 1,
    retryDelay: 1000,
  })
  
  // Mutation for creating a new session
  const createSessionMutation = useMutation<ChatSession, Error, string>({
    mutationFn: (name: string = "New Chat") => {
      // Ensure the API client has the auth context
      if (!auth.isAuthenticated || !auth.accessToken) {
        return Promise.reject(new Error("Not authenticated"))
      }
      // Ensure auth is set before making the request
      chatApi.setAuth(auth)
      return chatApi.createSession(name)
    },
    onSuccess: () => {
      // Invalidate and refetch the sessions list
      queryClient.invalidateQueries({ queryKey: ["chatSessions"] })
    },
    onError: (error) => {
      console.error("Error creating new chat session:", error)
    }
  })
  
  // Function to create a new chat session
  const createNewSession = async (name: string = "New Chat"): Promise<ChatSession> => {
    return new Promise((resolve, reject) => {
      createSessionMutation.mutate(name, {
        onSuccess: (data) => {
          resolve(data)
        },
        onError: (error) => {
          reject(error)
        }
      })
    })
  }
  
  return {
    sessions: sessionsQuery.data?.sessions || [],
    isLoading: sessionsQuery.isPending,
    isError: sessionsQuery.isError,
    error: sessionsQuery.error,
    createNewSession,
    isCreating: createSessionMutation.isPending
  }
}
