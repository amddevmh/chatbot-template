import { AppSidebar } from "@/components/app-sidebar";
import { AppRightSidebar } from "@/components/app-right-sidebar";
import { Chat } from "@/components/chat";
import { NutritionProvider } from "@/lib/context/nutrition-context";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbList,
  BreadcrumbPage,
} from "@/components/ui/breadcrumb";
import { Separator } from "@/components/ui/separator";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { ThemeProvider } from "./components/theme-provider";

export default function App() {
  // Control the visibility of sidebars
  const showLeftSidebar = true;
  const showRightSidebar = true;
  
  return (
    <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
      <NutritionProvider>
        <SidebarProvider
          showLeftSidebar={showLeftSidebar}
          showRightSidebar={showRightSidebar}
        >
        {showLeftSidebar && <AppSidebar />}
        <SidebarInset>
          <header className="sticky top-0 flex h-16 shrink-0 items-center gap-2 border-b bg-background px-4">
            {showLeftSidebar && (
              <>
                <SidebarTrigger side="left" className="-ml-1" />
                <Separator orientation="vertical" className="mr-2 h-4" />
              </>
            )}
            <Breadcrumb>
              <BreadcrumbList>
                <BreadcrumbItem>
                  <BreadcrumbPage>October 2024</BreadcrumbPage>
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
            <div className="flex-1" />
            {showRightSidebar && (
              <SidebarTrigger side="right" className="-mr-1" />
            )}
          </header>
          <div className="flex flex-1 flex-col h-[calc(100vh-4rem)]">
            <Chat />
          </div>
        </SidebarInset>
        {showRightSidebar && <AppRightSidebar />}
        </SidebarProvider>
      </NutritionProvider>
    </ThemeProvider>
  );
}
