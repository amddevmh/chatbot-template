import * as React from "react"
import { MessageSquare, Settings, User } from "lucide-react"

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
  SidebarSeparator,
} from "@/components/ui/sidebar"
import { Button } from "@/components/ui/button"

// This is sample data for the right sidebar
const data = {
  conversations: [
    "Chat with AI Assistant",
    "Project Planning",
    "Code Review Discussion",
    "Bug Fixing Session",
    "Feature Brainstorming"
  ],
}

export function AppRightSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar side="right" {...props}>
      <SidebarHeader className="h-16 border-b border-sidebar-border">
        <div className="flex items-center justify-between px-4 py-2">
          <h2 className="text-lg font-semibold">Conversations</h2>
          <Button variant="ghost" size="icon">
            <Settings className="h-5 w-5" />
          </Button>
        </div>
      </SidebarHeader>
      <SidebarContent>
        <div className="p-2">
          <Button className="w-full justify-start" variant="outline">
            <MessageSquare className="mr-2 h-4 w-4" />
            New Conversation
          </Button>
        </div>
        <SidebarSeparator className="mx-0" />
        <SidebarMenu>
          {data.conversations.map((conversation, index) => (
            <SidebarMenuItem key={index}>
              <SidebarMenuButton>
                <MessageSquare className="h-4 w-4" />
                <span>{conversation}</span>
              </SidebarMenuButton>
            </SidebarMenuItem>
          ))}
        </SidebarMenu>
      </SidebarContent>
      <SidebarFooter>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton>
              <User className="h-4 w-4" />
              <span>Profile Settings</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
      <SidebarRail side="right" />
    </Sidebar>
  )
}
