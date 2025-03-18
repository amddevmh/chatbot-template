import { useState, useEffect } from "react"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { chatApi } from "@/api-client"
import { useAuth } from "@/hooks/use-auth"

/**
 * Custom hook for managing the active chat session
 */
export function useActiveChat(sessionId?: string) {
  const auth = useAuth()
  const queryClient = useQueryClient()
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
      const refetchResult = await historyQuery.refetch()
      
      // Clear local messages as they should now be in the backend response
      setLocalMessages([])
      
      // Check if we should generate a title after first interaction is complete
      // We want to generate a title after we have at least 2 messages (1 from user, 1 from assistant)
      // Get the latest messages count from the refetched data
      const backendMessagesCount = refetchResult.data?.messages?.length || 0
      console.log('Backend messages count after refetch:', backendMessagesCount)
      
      // Generate title after first complete interaction (user message + AI response)
      if (activeSessionId && backendMessagesCount >= 2) {
        try {
          console.log("Generating title for session", activeSessionId)
          const updatedSession = await chatApi.generateSessionTitle(activeSessionId)
          
          // Optimistically update the sessions list
          queryClient.invalidateQueries({ queryKey: ["chatSessions"] })
          
          // Optionally, you can also update the current session data in the cache
          // This ensures the title is updated in all places that use this session
          if (updatedSession) {
            queryClient.setQueryData(
              ["chatSessions"], 
              (oldData: any) => {
                if (!oldData || !oldData.sessions) return oldData
                
                return {
                  ...oldData,
                  sessions: oldData.sessions.map((session: any) => 
                    session.session_id === activeSessionId 
                      ? { ...session, name: updatedSession.name }
                      : session
                  )
                }
              }
            )
          }
        } catch (titleError) {
          console.error("Error generating session title:", titleError)
        }
      }
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
  
  // Function to manually generate a title for the current session
  const generateTitle = async () => {
    if (!activeSessionId || !auth.isAuthenticated) return
    
    try {
      setIsLoading(true)
      
      // First, make sure we have the latest messages
      const refetchResult = await historyQuery.refetch()
      const backendMessagesCount = refetchResult.data?.messages?.length || 0
      console.log("Messages count before generating title:", backendMessagesCount)
      
      // Only proceed if we have at least 2 messages
      if (backendMessagesCount < 2) {
        console.warn("Not enough messages to generate a meaningful title")
        return null
      }
      
      console.log("Manually generating title for session", activeSessionId)
      const updatedSession = await chatApi.generateSessionTitle(activeSessionId)
      
      // Optimistically update the sessions list
      queryClient.invalidateQueries({ queryKey: ["chatSessions"] })
      
      // Update the current session data in the cache
      if (updatedSession) {
        queryClient.setQueryData(
          ["chatSessions"], 
          (oldData: any) => {
            if (!oldData || !oldData.sessions) return oldData
            
            return {
              ...oldData,
              sessions: oldData.sessions.map((session: any) => 
                session.session_id === activeSessionId 
                  ? { ...session, name: updatedSession.name }
                  : session
              )
            }
          }
        )
      }
      
      return updatedSession?.name
    } catch (error) {
      console.error("Error generating title:", error)
      return null
    } finally {
      setIsLoading(false)
    }
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
    initialLoadComplete,
    generateTitle // Expose the new function
  }
}
