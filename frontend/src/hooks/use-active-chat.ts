import { useState, useEffect } from "react"
import { useQuery } from "@tanstack/react-query"
import { chatApi } from "@/api-client"
import { useAuth } from "@/hooks/use-auth"

/**
 * Custom hook for managing the active chat session
 */
export function useActiveChat(sessionId?: string) {
  const auth = useAuth()
  const [activeSessionId, setActiveSessionId] = useState<string | undefined>(sessionId)
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [initialLoadComplete, setInitialLoadComplete] = useState(false)
  
  // Ensure chatApi has the latest auth context
  useEffect(() => {
    if (auth && auth.accessToken) {
      chatApi.setAuth(auth)
    }
  }, [auth, auth.isAuthenticated, auth.accessToken])
  
  // Query for fetching session history
  const historyQuery = useQuery({
    queryKey: ["chatHistory", activeSessionId, auth.isAuthenticated, auth.accessToken],
    queryFn: async () => {
      if (!auth.isAuthenticated || !auth.accessToken || !activeSessionId) {
        return { messages: [] }
      }
      // Ensure auth is set before making the request
      chatApi.setAuth(auth)
      return await chatApi.getSessionHistory(activeSessionId)
    },
    // Only fetch if we have an active session and user is authenticated
    enabled: !!activeSessionId && auth.isAuthenticated && !!auth.accessToken,
    // Retry failed queries
    retry: 1,
    retryDelay: 1000,
  })
  
  // Set initial load complete when the query is settled (either success or error)
  useEffect(() => {
    if (historyQuery.isSuccess || historyQuery.isError) {
      // Add a small delay to prevent flashing states
      const timer = setTimeout(() => {
        setInitialLoadComplete(true)
      }, 300)
      
      return () => clearTimeout(timer)
    }
  }, [historyQuery.isSuccess, historyQuery.isError])
  
  // Local state for messages before backend sync
  const [localMessages, setLocalMessages] = useState<any[]>([])

  // Combine backend messages with local ones that haven't been synced yet
  const combinedMessages = [...(historyQuery.data?.messages || []), ...localMessages]

  // Function to send a message
  const sendMessage = async () => {
    if (!input.trim() || isLoading || !auth.isAuthenticated) return
    
    // Create a temporary message to show immediately
    const tempMessage = {
      id: `temp-${Date.now()}`,
      content: input.trim(),
      role: "human",
      timestamp: new Date().toISOString(),
    }
    
    // Add to local messages immediately
    setLocalMessages(prev => [...prev, tempMessage])
    
    // Clear input field right away
    setInput("")
    
    setIsLoading(true)
    try {
      // Send to backend
      await chatApi.sendMessage(tempMessage.content, activeSessionId)
      
      // Refetch the messages after sending
      await historyQuery.refetch()
      
      // Clear local messages as they should now be in the backend response
      setLocalMessages([])
    } catch (error) {
      console.error("Error sending message:", error)
    } finally {
      setIsLoading(false)
    }
  }
  
  // Function to set the active session
  const setActiveSession = (sessionId: string) => {
    setActiveSessionId(sessionId)
  }
  
  return {
    activeSessionId,
    setActiveSession,
    messages: combinedMessages,
    isLoading: (historyQuery.isPending && !initialLoadComplete) || isLoading,
    isInitialLoading: historyQuery.isPending && !initialLoadComplete,
    isError: historyQuery.isError,
    error: historyQuery.error,
    input,
    setInput,
    sendMessage,
    isSending: isLoading,
    initialLoadComplete
  }
}
