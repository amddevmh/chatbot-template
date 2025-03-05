import * as React from "react"
import { Send } from "lucide-react"
import OpenAI from "openai"

import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { ScrollArea } from "@/components/ui/scroll-area"
import { cn } from "@/lib/utils"
import { sendChatMessage, extractNutritionInfo } from "@/lib/services/openai"
import { useNutrition } from "@/lib/context/nutrition-context"

// Typing indicator component with animated dots
function TypingIndicator() {
  const [dots, setDots] = React.useState(".")
  
  React.useEffect(() => {
    const interval = setInterval(() => {
      setDots(prev => prev.length >= 3 ? "." : prev + ".")
    }, 500)
    
    return () => clearInterval(interval)
  }, [])
  
  return (
    <div className="flex max-w-[80%] flex-col gap-2 rounded-lg px-3 py-2 text-sm bg-muted">
      <div className="flex items-center gap-2">
        <Avatar className="h-6 w-6 shrink-0">
          <AvatarFallback>AI</AvatarFallback>
        </Avatar>
        <div className="font-medium">Typing{dots}</div>
      </div>
    </div>
  )
}

// Message type definition
interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
}

export function Chat() {
  const { addMeal } = useNutrition()
  const [messages, setMessages] = React.useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content: "Hello! I'm your nutrition assistant. I can help you track your meals and provide nutrition information. Tell me what you've eaten today, and I'll help track your nutrition goals. Please keep our conversation focused on nutrition and health topics.",
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = React.useState("")
  const [isLoading, setIsLoading] = React.useState(false)
  const messagesEndRef = React.useRef<HTMLDivElement>(null)

  // Scroll to bottom when messages change
  React.useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  // Nutrition info state to hold pending confirmations
  const [pendingNutritionInfo, setPendingNutritionInfo] = React.useState<{
    info: any;
    confirmed: boolean;
    messageId: string;
  } | null>(null);

  // Handle user confirming nutrition data
  const handleNutritionConfirmation = (confirmed: boolean) => {
    if (!pendingNutritionInfo) return;
    
    if (confirmed && pendingNutritionInfo.info?.foodItems) {
      // Add the entire meal to the nutrition tracker
      const mealName = pendingNutritionInfo.info.mealName || "Unknown Meal";
      const foodItems = pendingNutritionInfo.info.foodItems;
      
      // Add all items as a single meal
      addMeal(mealName, foodItems);
      
      // Add confirmation message
      const confirmMessage: Message = {
        id: Date.now().toString(),
        role: "assistant",
        content: `I've added your ${mealName.toLowerCase()} to your nutrition tracker.`,
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, confirmMessage]);
    } else {
      // Add cancellation message
      const cancelMessage: Message = {
        id: Date.now().toString(),
        role: "assistant",
        content: "I won't update your nutrition tracker. Let me know if you want to try again with more specific information.",
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, cancelMessage]);
    }
    
    // Clear pending nutrition info
    setPendingNutritionInfo(null);
  };

  // Handle sending a message
  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    // If this is a confirmation response to pending nutrition
    if (pendingNutritionInfo && !pendingNutritionInfo.confirmed) {
      const lowercaseInput = input.trim().toLowerCase();
      if (lowercaseInput.includes('yes') || lowercaseInput.includes('confirm') || lowercaseInput.includes('correct')) {
        // Add user message
        const userMessage: Message = {
          id: Date.now().toString(),
          role: "user",
          content: input.trim(),
          timestamp: new Date(),
        };
        
        setMessages(prev => [...prev, userMessage]);
        setInput("");
        
        // Process confirmation
        handleNutritionConfirmation(true);
        return;
      } else if (lowercaseInput.includes('no') || lowercaseInput.includes('cancel') || lowercaseInput.includes('incorrect')) {
        // Add user message
        const userMessage: Message = {
          id: Date.now().toString(),
          role: "user",
          content: input.trim(),
          timestamp: new Date(),
        };
        
        setMessages(prev => [...prev, userMessage]);
        setInput("");
        
        // Process cancellation
        handleNutritionConfirmation(false);
        return;
      }
      // If it's not a clear yes/no, continue with normal processing
    }

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input.trim(),
      timestamp: new Date(),
    };
    
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      // Extract nutrition information from the user message
      const nutritionInfo = await extractNutritionInfo(userMessage.content);
      
      // If we got valid nutrition info, prepare for confirmation
      const hasNutritionInfo = nutritionInfo?.foodItems && nutritionInfo.foodItems.length > 0;

      // Add system instruction about nutrition confirmation if we have nutrition data
      const systemContent = hasNutritionInfo
        ? "You are a helpful nutrition assistant. You help users track their food intake and provide nutritional advice. Be friendly, supportive, and concise. I have extracted nutrition information from the user's input. Ask the user to confirm if the nutrition information looks correct before updating their tracker. DO NOT update their nutrition information until they confirm. If the user asks about topics unrelated to nutrition, food, health, or the nutrition tracking app, politely redirect them back to nutrition-related topics by saying something like 'Let's focus on your nutrition goals. Is there anything specific about your diet or nutrition that I can help with?'"
        : "You are a helpful nutrition assistant. You help users track their food intake and provide nutritional advice. Be friendly, supportive, and concise. If the user mentions food, ask for specific details like portion size, preparation method, and specific ingredients. If the user asks about topics unrelated to nutrition, food, health, or the nutrition tracking app, politely redirect them back to nutrition-related topics by saying something like 'Let's focus on your nutrition goals. Is there anything specific about your diet or nutrition that I can help with?'"

      // Convert message history to OpenAI format
      const messageHistory: OpenAI.Chat.ChatCompletionMessageParam[] = [
        {
          role: "system" as const,
          content: systemContent
        },
        ...messages.map(msg => {
          // Convert our message roles to OpenAI's expected types
          const role: OpenAI.Chat.ChatCompletionMessageParam["role"] = 
            msg.role === "user" ? "user" : "assistant";
          return {
            role,
            content: msg.content
          };
        }),
        { role: "user" as const, content: userMessage.content }
      ]

      // If we have nutrition info, add it as a system message
      if (hasNutritionInfo) {
        const mealName = nutritionInfo.mealName || "Unknown Meal";
        const itemsDescription = nutritionInfo.foodItems.map(item => 
          `${item.name}: ${item.calories} calories, ${item.protein || 0}g protein, ${item.carbs || 0}g carbs, ${item.fat || 0}g fat`
        ).join("; ");
        
        messageHistory.push({
          role: "system" as const,
          content: `I have extracted the following nutrition information for ${mealName}: ${itemsDescription}. Ask the user to confirm if this information is correct before updating their tracker.`
        });
      }

      // Get response from OpenAI
      const response = await sendChatMessage(messageHistory);

      // Add assistant response
      const assistantMessage: Message = {
        id: Date.now().toString(),
        role: "assistant",
        content: response,
        timestamp: new Date(),
      };
      
      setMessages((prev) => [...prev, assistantMessage]);
      
      // Store nutrition info as pending if we have any
      if (hasNutritionInfo) {
        setPendingNutritionInfo({
          info: nutritionInfo,
          confirmed: false,
          messageId: assistantMessage.id
        });
      }
    } catch (error) {
      console.error("Error processing message:", error)
      
      // Add error message if something went wrong
      const errorMessage: Message = {
        id: Date.now().toString(),
        role: "assistant",
        content: "I'm sorry, I encountered an error processing your request. Please try again.",
        timestamp: new Date(),
      }
      
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  // Handle key press (send on Enter, but allow Shift+Enter for new lines)
  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 overflow-hidden">
        <ScrollArea className="h-full">
          <div className="flex flex-col gap-4 p-4 w-full">
            {messages.map((message) => (
              <div
                key={message.id}
                className={cn(
                  "flex max-w-[80%] flex-col gap-2 rounded-lg px-3 py-2 text-sm",
                  message.role === "user"
                    ? "ml-auto bg-primary text-primary-foreground"
                    : "bg-muted"
                )}
              >
                <div className="flex items-center gap-2">
                  {message.role === "assistant" && (
                    <Avatar className="h-6 w-6 shrink-0">
                      <AvatarFallback>AI</AvatarFallback>
                    </Avatar>
                  )}
                  <div className="break-words">{message.content}</div>
                </div>
                <div
                  className={cn(
                    "text-xs opacity-70",
                    message.role === "user" ? "text-right" : "text-left"
                  )}
                >
                  {message.timestamp.toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </div>
              </div>
            ))}
            {isLoading && <TypingIndicator />}
            <div ref={messagesEndRef} />
          </div>
        </ScrollArea>
      </div>
      <div className="border-t bg-background p-4">
        <div className="flex items-center gap-2">
          <Textarea
            className="min-h-10 flex-1 resize-none"
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
          />
          <Button size="icon" onClick={handleSend} disabled={!input.trim() || isLoading}>
            <Send className="h-4 w-4" />
            <span className="sr-only">Send</span>
          </Button>
        </div>
      </div>
    </div>
  )
}
