import * as React from "react"
import { format } from "date-fns"
import { MessageSquare, Plus, Loader2 } from "lucide-react"
import { useNavigate } from "react-router-dom"

import { NavUser } from "@/components/nav-user"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
} from "@/components/ui/sidebar"
import { Skeleton } from "@/components/ui/skeleton"
import { useChatSessions } from "@/hooks/use-chat-sessions"
import { ChatSession } from "@/types"

interface AppSidebarProps extends React.ComponentProps<typeof Sidebar> {
  onSessionSelect?: (sessionId: string, sessionName: string) => void;
  activeSessionId?: string;
}

export function AppSidebar({ 
  onSessionSelect, 
  activeSessionId, 
  ...props 
}: AppSidebarProps) {
  const navigate = useNavigate()
  // Use our custom hook to manage chat sessions
  const { 
    sessions, 
    isLoading, 
    isError, 
    error, 
    createNewSession, 
    isCreating 
  } = useChatSessions()
  
  // Explicitly type the sessions array
  const typedSessions: ChatSession[] = sessions

  return (
    <Sidebar className="h-screen bg-sidebar-background" {...props}>
      <SidebarHeader className="h-16 border-b border-sidebar-border bg-sidebar-background/90 backdrop-blur-sm sticky top-0 z-10">
        <NavUser />
      </SidebarHeader>
      <SidebarContent className="h-[calc(100vh-120px)] overflow-y-auto px-1 py-2">
        {/* Using React 19's more declarative approach to conditional rendering */}
        {isLoading && (
          // Show loading state
          <div className="space-y-3 p-3">
            <Skeleton className="h-14 w-full rounded-lg opacity-70" />
            <Skeleton className="h-14 w-full rounded-lg opacity-60" />
            <Skeleton className="h-14 w-full rounded-lg opacity-50" />
          </div>
        )}
        
        {isError && (
          // Show error state
          <div className="p-4 m-2 text-destructive bg-destructive/10 rounded-lg border border-destructive/20">
            <p className="font-medium mb-1">Error loading sessions</p>
            <p className="text-sm">{(error as Error)?.message || "Unknown error"}</p>
          </div>
        )}
        
        {!isLoading && !isError && (
          // Show sessions list
          <SidebarMenu className="gap-3 py-2">
            {typedSessions && typedSessions.length > 0 ? (
              typedSessions.map((session) => (
                <SidebarMenuItem key={session.session_id} className="mb-1">
                  <SidebarMenuButton 
                    onClick={() => {
                      if (onSessionSelect) {
                        onSessionSelect(session.session_id, session.name);
                      } else {
                        navigate(`/chat/${session.session_id}`);
                      }
                    }}
                    className={`rounded-lg transition-all duration-200 hover:bg-sidebar-accent py-3 ${activeSessionId === session.session_id ? "bg-sidebar-accent border-l-2 border-primary" : ""}`}
                  >
                    <MessageSquare className={`h-4 w-4 ${activeSessionId === session.session_id ? "text-primary" : "text-sidebar-foreground/70"}`} />
                    <div className="flex flex-col items-start">
                      <span className={`text-sm font-medium ${activeSessionId === session.session_id ? "text-sidebar-foreground" : "text-sidebar-foreground/90"}`}>{session.name}</span>
                      <span className="text-xs text-sidebar-foreground/60">
                        {format(new Date(session.updated_at), "MMM d, yyyy")} · {session.message_count} messages
                      </span>
                    </div>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))
            ) : (
              <div className="p-6 text-center text-sidebar-foreground/60 bg-sidebar-accent/50 rounded-lg m-2">
                <p className="text-sm">No chat sessions found</p>
                <p className="text-xs mt-1">Create a new chat to get started</p>
              </div>
            )}
          </SidebarMenu>
        )}
      </SidebarContent>
      <SidebarFooter className="border-t border-sidebar-border bg-sidebar-background/90 backdrop-blur-sm sticky bottom-0 pb-1 pt-2">
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton 
              onClick={async () => {
                try {
                  // Create new session and get the returned session directly
                  const newSession = await createNewSession("New Chat");
                  // Navigate directly to the newly created session
                  navigate(`/chat/${newSession.session_id}`);
                } catch (error) {
                  console.error("Error creating new session:", error);
                }
              }} 
              disabled={isCreating}
              className="bg-sidebar-primary hover:bg-sidebar-primary/90 text-sidebar-primary-foreground rounded-lg font-medium transition-all duration-200 shadow-sm hover:shadow py-3 my-1"
            >
              {isCreating ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Plus className="h-4 w-4" />
              )}
              <span>New Chat</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  )
}
