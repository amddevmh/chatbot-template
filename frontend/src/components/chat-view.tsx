import * as React from "react"
import { useParams, useNavigate } from "react-router-dom"
import { AppSidebar } from "@/components/app-sidebar"
import { Chat } from "@/components/chat"
import { 
  SidebarProvider,
  SidebarInset,
  SidebarTrigger 
} from "@/components/ui/sidebar"
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbList,
  BreadcrumbPage,
} from "@/components/ui/breadcrumb"
import { Separator } from "@/components/ui/separator"
import { useChatSessions } from "@/hooks/use-chat-sessions"

export function ChatView() {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const { sessions } = useChatSessions();
  const showLeftSidebar = true;
  
  // Find the active session from the URL parameter
  const activeSession = React.useMemo(() => {
    if (!sessionId || !sessions) return null;
    const session = sessions.find(s => s.session_id === sessionId);
    return session ? { id: session.session_id, name: session.name } : null;
  }, [sessionId, sessions]);
  
  // Handle invalid session IDs
  const [isInvalidSession, setIsInvalidSession] = React.useState(false);
  
  React.useEffect(() => {
    // If we have a sessionId but no matching session after sessions are loaded
    if (sessionId && sessions && sessions.length > 0 && !activeSession) {
      setIsInvalidSession(true);
    } else {
      setIsInvalidSession(false);
    }
  }, [sessionId, sessions, activeSession]);

  // Handle session selection by navigating to the session URL
  const handleSessionSelect = (sessionId: string, _sessionName: string) => {
    navigate(`/chat/${sessionId}`);
  }

  return (
    <div className="h-screen w-screen overflow-hidden">
      <SidebarProvider
        showLeftSidebar={showLeftSidebar}
        showRightSidebar={false}
      >
        {showLeftSidebar && (
          <AppSidebar 
            onSessionSelect={handleSessionSelect}
            activeSessionId={activeSession?.id}
          />
        )}
        
        <SidebarInset>
          <header className="sticky top-0 flex h-16 shrink-0 items-center gap-2 border-b bg-background/90 backdrop-blur-sm px-4 z-10 shadow-sm">
            {showLeftSidebar && (
              <>
                <SidebarTrigger side="left" className="-ml-1 hover:bg-muted/80 transition-colors" />
                <Separator orientation="vertical" className="mr-2 h-5 opacity-30" />
              </>
            )}
            <Breadcrumb>
              <BreadcrumbList>
                <BreadcrumbItem>
                  <BreadcrumbPage className="font-medium text-lg flex items-center gap-2">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-5 w-5 text-primary">
                      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                    </svg>
                    {activeSession ? activeSession.name : "Chat App"}
                  </BreadcrumbPage>
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
            <div className="flex-1" />
          </header>
          
          <div className="flex flex-1 flex-col h-[calc(100vh-4rem)]">
            {isInvalidSession ? (
              <div className="flex h-full w-full items-center justify-center p-8 text-center">
                <div className="max-w-md space-y-6 bg-card/30 backdrop-blur-sm p-8 rounded-xl border border-border/40 shadow-sm">
                  <div className="flex flex-col items-center gap-2">
                    <div className="h-16 w-16 rounded-full bg-destructive/10 flex items-center justify-center text-destructive">
                      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-8 w-8">
                        <path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                        <line x1="12" y1="9" x2="12" y2="13"/>
                        <line x1="12" y1="17" x2="12.01" y2="17"/>
                      </svg>
                    </div>
                    <h3 className="text-xl font-semibold text-destructive">Chat not found</h3>
                  </div>
                  <p className="text-muted-foreground">
                    The chat session you're looking for doesn't exist or has been deleted.
                  </p>
                  <button 
                    onClick={() => navigate('/chat')} 
                    className="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-6 py-2 w-full"
                  >
                    Go back to chat list
                  </button>
                </div>
              </div>
            ) : sessionId && activeSession ? (
              <Chat 
                sessionId={sessionId}
                sessionName={activeSession.name}
              />
            ) : (
              <div className="flex h-full w-full items-center justify-center p-8 text-center">
                <div className="max-w-md space-y-6 bg-card/30 backdrop-blur-sm p-8 rounded-xl border border-border/40 shadow-sm">
                  <div className="flex flex-col items-center gap-2">
                    <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-8 w-8">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                      </svg>
                    </div>
                    <h3 className="text-xl font-semibold">Welcome to Chat App</h3>
                  </div>
                  <p className="text-muted-foreground">
                    Select a chat from the sidebar or create a new one to get started with your AI assistant.
                  </p>
                  <button 
                    onClick={() => navigate('/chat/new')} 
                    className="inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-6 py-2 w-full"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4">
                      <line x1="12" y1="5" x2="12" y2="19"/>
                      <line x1="5" y1="12" x2="19" y2="12"/>
                    </svg>
                    Start a new chat
                  </button>
                </div>
              </div>
            )}
          </div>
        </SidebarInset>
      </SidebarProvider>
    </div>
  )
}
