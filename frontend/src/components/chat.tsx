import * as React from "react";
import { Send, Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import { useActiveChat } from "@/hooks/use-active-chat";
import { ChatMessage } from "@/types";

// Typing indicator component with animated dots
function TypingIndicator() {
  return (
    <div className="flex flex-col gap-2 rounded-lg px-4 py-2 text-sm bg-muted/40 backdrop-blur-sm shadow-sm border border-border/20 ml-2 w-fit max-w-[90%]">
      <div className="flex items-center gap-2">
        <div className="font-medium flex items-center gap-1 text-foreground/70 flex-wrap">
          <span>Thinking</span>
          <span className="inline-flex">
            <span className="animate-bounce delay-0 mx-[1px]">.</span>
            <span className="animate-bounce delay-100 mx-[1px]">.</span>
            <span className="animate-bounce delay-200 mx-[1px]">.</span>
          </span>
        </div>
      </div>
    </div>
  );
}

interface ChatProps {
  sessionId?: string;
  sessionName?: string;
}

export function Chat({ sessionId, sessionName = "Chat" }: ChatProps) {
  const {
    activeSessionId,
    setActiveSession,
    messages,
    isLoading,
    isInitialLoading,
    input,
    setInput,
    sendMessage,
    isSending,
  } = useActiveChat(sessionId);

  // Explicitly type the messages array
  const typedMessages: ChatMessage[] = messages;

  const messagesEndRef = React.useRef<HTMLDivElement>(null);

  // Set active session when sessionId changes
  React.useEffect(() => {
    if (sessionId) {
      setActiveSession(sessionId);
    }
  }, [sessionId, setActiveSession]);

  // Scroll to bottom when messages change
  React.useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Handle key press (send on Enter, but allow Shift+Enter for new lines)
  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Show a loading state while the chat is initializing
  if (isInitialLoading) {
    return (
      <div className="flex h-full w-full flex-col">
        <div className="border-b p-4 bg-background z-10 sticky top-0">
          <h2 className="text-xl font-semibold">{sessionName}</h2>
        </div>
        <div className="flex h-[calc(100vh-180px)] items-center justify-center">
          <div className="flex flex-col items-center space-y-4 text-center">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <p className="text-muted-foreground">Loading chat messages...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full w-full flex-col overflow-hidden">
      {/* Message area with scroll */}
      <div className="flex-1 overflow-hidden">
        <ScrollArea className="h-[calc(100vh-180px)]" type="auto">
          <div className={`flex flex-col gap-6 p-4 sm:p-6 pt-6 pb-8 w-full ${messages.length > 0 ? 'min-h-[calc(100vh-180px)]' : 'h-[calc(100vh-180px)]'} items-stretch overflow-hidden`}>
            {messages.length === 0 && (
              <div className="flex items-center justify-center text-center h-full">
                <div className="max-w-md space-y-6 bg-card/30 backdrop-blur-sm p-8 rounded-xl border border-border/40 shadow-sm">
                  <div className="flex flex-col items-center gap-2">
                    <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="24"
                        height="24"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        className="h-8 w-8"
                      >
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                      </svg>
                    </div>
                    <h3 className="text-xl font-semibold">
                      Start a new conversation
                    </h3>
                  </div>
                  <p className="text-muted-foreground">
                    Type a message below to begin chatting with your AI
                    assistant.
                  </p>
                </div>
              </div>
            )}

            {typedMessages.map((message) => (
              <div
                key={message.id}
                className={cn(
                  "w-full flex",
                  message.role === "human" ? "justify-end" : "justify-start"
                )}
              >
                <div
                  className={cn(
                    "flex flex-col gap-3 rounded-lg px-5 py-4 text-sm max-w-[80%] transition-all overflow-hidden",
                    message.role === "human"
                      ? "bg-primary text-primary-foreground shadow-sm animate-in slide-in-from-right-5 duration-300"
                      : "bg-card border border-border/30 shadow-sm animate-in slide-in-from-left-5 duration-300"
                  )}
                >
                  {message.role === "human" ? (
                    <div>
                      <div className="break-words overflow-hidden whitespace-pre-wrap">
                        {message.content}
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-start gap-2">
                      <div className="break-words overflow-hidden whitespace-pre-wrap">
                        {message.content}
                      </div>
                    </div>
                  )}
                  <div
                    className={cn(
                      "text-xs opacity-70 mt-2",
                      message.role === "human" ? "text-right" : "text-left"
                    )}
                  >
                    {new Date(message.timestamp).toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </div>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />

            {/* Fixed-height container for typing indicator to prevent layout shifts */}
            {isLoading && (
              <div className="h-16 relative">
                <div className="absolute top-0 left-0">
                  <TypingIndicator />
                </div>
              </div>
            )}
          </div>
        </ScrollArea>
      </div>
      {/* Input area - outside of scroll area */}
      <div className="border-t bg-background/90 backdrop-blur-sm p-4 sm:p-5 shadow-[0_-2px_10px_rgba(0,0,0,0.05)] w-full z-10 flex items-center">
        <div className="flex items-center gap-2 sm:gap-3 max-w-4xl mx-auto w-full">
          <Textarea
            className="min-h-10 flex-1 resize-none py-2 sm:py-3 px-3 sm:px-4 rounded-xl border-muted bg-background/80 focus-visible:ring-primary/50 shadow-sm text-sm sm:text-base w-full"
            placeholder="Ask me anything..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
            disabled={!activeSessionId || isSending}
          />
          <Button
            size="icon"
            onClick={sendMessage}
            disabled={!input.trim() || isSending || !activeSessionId}
            className="bg-primary hover:bg-primary/90 text-primary-foreground rounded-full w-10 h-10 shadow-sm transition-all duration-200"
          >
            {isSending ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              <Send className="h-5 w-5" />
            )}
            <span className="sr-only">Send</span>
          </Button>
        </div>
      </div>
    </div>
  );
}
