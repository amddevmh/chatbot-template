import * as React from "react"
import { Send } from "lucide-react"
import OpenAI from "openai"

import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { ScrollArea } from "@/components/ui/scroll-area"
import { cn } from "@/lib/utils"
import { sendChatMessage, extractNutritionInfo, NutritionInfo } from "@/lib/services/openai"
import { useNutrition } from "@/lib/context/nutrition-context"
import ReactMarkdown from "react-markdown"

// Format nutrition information in a readable way using markdown
function formatNutritionResponse(nutritionInfo: NutritionInfo): string {
  let response = `## Nutrition Information for ${nutritionInfo.mealName || 'Your Meal'}

`;
  
  // Calculate total calories and macros
  const totalCalories = nutritionInfo.foodItems.reduce((sum, item) => sum + item.calories, 0);
  const totalProtein = nutritionInfo.foodItems.reduce((sum, item) => sum + (item.protein || 0), 0);
  const totalCarbs = nutritionInfo.foodItems.reduce((sum, item) => sum + (item.carbs || 0), 0);
  const totalFat = nutritionInfo.foodItems.reduce((sum, item) => sum + (item.fat || 0), 0);
  
  // Add summary section with better spacing
  response += `### Summary

`;
  response += `**Total Calories:** ${totalCalories} kcal  

`;
  response += `**Total Macros:**  
- Protein: ${totalProtein.toFixed(1)}g  
- Carbs: ${totalCarbs.toFixed(1)}g  
- Fat: ${totalFat.toFixed(1)}g  

`;
  
  // Add horizontal rule for visual separation
  response += `---

`;
  
  // Add detailed breakdown with improved spacing
  response += `### Detailed Breakdown

`;
  
  nutritionInfo.foodItems.forEach((item, index) => {
    // Add separator between food items
    if (index > 0) {
      response += `---

`;
    }
    
    response += `#### ${item.name}

`;
    response += `**Calories:** ${item.calories} kcal\n\n`;
    
    // Group macros together with better formatting
    response += `**Macros:**  \n`;
    if (item.protein) response += `- Protein: ${item.protein}g  \n`;
    if (item.carbs) response += `- Carbs: ${item.carbs}g  \n`;
    if (item.fat) response += `- Fat: ${item.fat}g  \n`;
    if (item.fiber) response += `- Fiber: ${item.fiber}g  \n`;
    
    response += '\n';
    
    // Add micronutrients if available with better spacing and formatting
    const hasMicronutrients = item.vitaminD || item.iron || item.calcium || item.potassium;
    if (hasMicronutrients) {
      response += `**Micronutrients:**  \n`;
      if (item.vitaminD) response += `- Vitamin D: ${item.vitaminD}μg  \n`;
      if (item.iron) response += `- Iron: ${item.iron}mg  \n`;
      if (item.calcium) response += `- Calcium: ${item.calcium}mg  \n`;
      if (item.potassium) response += `- Potassium: ${item.potassium}mg  \n`;
      response += '\n';
    }
  });
  
  // Add a final horizontal rule
  response += `---

`;
  
  response += `Does this look correct? Once you confirm, I'll update your tracker accordingly.`;
  
  return response;
}

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
        ? "You are a helpful nutrition assistant. You help users track their food intake and provide nutritional advice. Be friendly, supportive, and concise. Format your responses using markdown for better readability - use headings (##), bullet points, bold text (**text**), and other formatting to make information clear and organized. I have extracted nutrition information from the user's input. Ask the user to confirm if the nutrition information looks correct before updating their tracker. DO NOT update their nutrition information until they confirm. If the user asks about topics unrelated to nutrition, food, health, or the nutrition tracking app, politely redirect them back to nutrition-related topics by saying something like 'Let's focus on your nutrition goals. Is there anything specific about your diet or nutrition that I can help with?'"
        : "You are a helpful nutrition assistant. You help users track their food intake and provide nutritional advice. Be friendly, supportive, and concise. Format your responses using markdown for better readability - use headings (##), bullet points, bold text (**text**), and other formatting to make information clear and organized. If the user mentions food, ask for specific details like portion size, preparation method, and specific ingredients. If the user asks about topics unrelated to nutrition, food, health, or the nutrition tracking app, politely redirect them back to nutrition-related topics by saying something like 'Let's focus on your nutrition goals. Is there anything specific about your diet or nutrition that I can help with?'"

      // Add custom styles to the document for better markdown rendering if not already added
      if (!document.getElementById('nutrition-markdown-styles')) {
        const style = document.createElement('style');
        style.id = 'nutrition-markdown-styles';
        style.innerHTML = `
          .nutrition-message h2 { margin-top: 0.5rem; margin-bottom: 1rem; font-size: 1.25rem; }
          .nutrition-message h3 { margin-top: 1.5rem; margin-bottom: 0.75rem; font-size: 1.1rem; }
          .nutrition-message h4 { margin-top: 1.25rem; margin-bottom: 0.5rem; font-size: 1rem; }
          .nutrition-message hr { height: 1px; background-color: rgba(100, 100, 100, 0.2); border: none; margin: 1rem 0; }
          .nutrition-message ul, .nutrition-message ol { margin-top: 0.5rem; padding-left: 1.5rem; }
          .nutrition-message li { margin-bottom: 0.375rem; }
          .nutrition-message p { margin: 0.5rem 0; }
        `;
        document.head.appendChild(style);
      }
      
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
        // Format nutrition information in a more readable way
        const formattedNutrition = formatNutritionResponse(nutritionInfo);
        
        messageHistory.push({
          role: "system" as const,
          content: `I have extracted nutrition information from the user's message. Present this information to the user in a clear, formatted way and ask them to confirm if it's correct: ${formattedNutrition}`
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
      
      // If we have nutrition info, replace the response with our formatted version
      if (hasNutritionInfo) {
        assistantMessage.content = formatNutritionResponse(nutritionInfo);
      }
      
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
          <div className="flex flex-col gap-5 p-4 w-full">
            {messages.map((message) => (
              <div
                key={message.id}
                className={cn(
                  "flex max-w-[90%] flex-col gap-3 rounded-lg px-5 py-4 text-sm",
                  message.role === "user"
                    ? "ml-auto bg-primary text-primary-foreground"
                    : "bg-card shadow-sm border border-border/30"
                )}
              >
                <div className="flex items-center gap-2">
                  {message.role === "assistant" && (
                    <Avatar className="h-6 w-6 shrink-0">
                      <AvatarFallback>AI</AvatarFallback>
                    </Avatar>
                  )}
                  <div className={cn(
                    "break-words w-full",
                    message.role === "assistant" ? "prose dark:prose-invert prose-sm max-w-none prose-headings:font-semibold prose-headings:text-foreground prose-p:text-foreground/90 prose-strong:text-foreground prose-strong:font-semibold prose-hr:my-4 prose-li:my-0 prose-li:mb-1 prose-p:my-2 nutrition-message" : ""
                  )}>
                    {message.role === "assistant" ? (
                      <ReactMarkdown>
                        {message.content}
                      </ReactMarkdown>
                    ) : (
                      message.content
                    )}
                  </div>
                </div>
                <div
                  className={cn(
                    "text-xs opacity-70 mt-1",
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
