import * as React from "react"
import { Apple, Dumbbell, Droplet, Flame, Leaf, Utensils } from "lucide-react"

import {
  Sidebar,
  SidebarContent,
  SidebarHeader,
  SidebarRail,
  SidebarSeparator,
} from "@/components/ui/sidebar"
import { Progress } from "@/components/ui/progress"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

// Mock data for nutrition tracking
const nutritionData = {
  calories: {
    current: 1450,
    target: 2000,
    unit: "kcal"
  },
  macros: [
    { name: "Protein", current: 85, target: 120, unit: "g", color: "bg-blue-500" },
    { name: "Carbs", current: 160, target: 250, unit: "g", color: "bg-amber-500" },
    { name: "Fat", current: 45, target: 65, unit: "g", color: "bg-rose-500" },
    { name: "Fiber", current: 18, target: 30, unit: "g", color: "bg-green-500" },
  ],
  micronutrients: [
    { name: "Vitamin D", current: 10, target: 15, unit: "μg", color: "bg-yellow-500" },
    { name: "Iron", current: 6, target: 18, unit: "mg", color: "bg-red-500" },
    { name: "Calcium", current: 650, target: 1000, unit: "mg", color: "bg-slate-400" },
    { name: "Potassium", current: 2100, target: 3500, unit: "mg", color: "bg-purple-500" },
  ],
  water: {
    current: 1.2,
    target: 2.5,
    unit: "L"
  }
}

// Helper function to get icon for each macro
const getMacroIcon = (name: string) => {
  switch (name.toLowerCase()) {
    case "protein":
      return <Dumbbell className="h-4 w-4 text-blue-500" />
    case "carbs":
      return <Apple className="h-4 w-4 text-amber-500" />
    case "fat":
      return <Flame className="h-4 w-4 text-rose-500" />
    case "fiber":
      return <Leaf className="h-4 w-4 text-green-500" />
    default:
      return <Utensils className="h-4 w-4" />
  }
}

// Progress bar component with label and values
function NutritionProgressBar({ 
  name, 
  current, 
  target, 
  unit, 
  color, 
  icon 
}: { 
  name: string; 
  current: number; 
  target: number; 
  unit: string; 
  color: string; 
  icon?: React.ReactNode 
}) {
  const percentage = Math.min(Math.round((current / target) * 100), 100)
  
  return (
    <div className="mb-3">
      <div className="flex items-center justify-between mb-1">
        <div className="flex items-center gap-1.5">
          {icon}
          <span className="text-sm font-medium">{name}</span>
        </div>
        <div className="text-xs text-muted-foreground">
          {current}{unit} / {target}{unit}
          <Badge variant="outline" className="ml-2 px-1 py-0 h-4">
            {percentage}%
          </Badge>
        </div>
      </div>
      <Progress 
        value={percentage} 
        className={`h-2 ${color}`}
      />
    </div>
  )
}

export function AppRightSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar side="right" {...props}>
      <SidebarHeader className="h-16 border-b border-sidebar-border">
        <div className="flex items-center justify-between px-4 py-2">
          <h2 className="text-lg font-semibold">Nutrition Tracker</h2>
          <Badge variant="outline" className="text-xs">
            Today
          </Badge>
        </div>
      </SidebarHeader>
      <SidebarContent className="px-4 py-4">
        {/* Calories Card */}
        <Card className="mb-4 border-none shadow-sm bg-gradient-to-br from-primary/5 to-primary/10">
          <CardHeader className="pb-2 pt-4">
            <CardTitle className="text-base flex items-center gap-2">
              <Flame className="h-5 w-5 text-primary" />
              Daily Calories
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-end justify-between mb-2">
              <div className="text-3xl font-bold">
                {nutritionData.calories.current}
                <span className="text-sm font-normal ml-1 text-muted-foreground">
                  {nutritionData.calories.unit}
                </span>
              </div>
              <div className="text-sm text-muted-foreground">
                Target: {nutritionData.calories.target} {nutritionData.calories.unit}
              </div>
            </div>
            <Progress 
              value={(nutritionData.calories.current / nutritionData.calories.target) * 100} 
              className="h-3 bg-primary/20"
            />
          </CardContent>
        </Card>

        {/* Macronutrients Section */}
        <div className="mb-6">
          <h3 className="text-sm font-semibold mb-3 text-muted-foreground uppercase tracking-wider">Macronutrients</h3>
          {nutritionData.macros.map((macro) => (
            <NutritionProgressBar
              key={macro.name}
              name={macro.name}
              current={macro.current}
              target={macro.target}
              unit={macro.unit}
              color={macro.color}
              icon={getMacroIcon(macro.name)}
            />
          ))}
        </div>

        <SidebarSeparator className="my-4" />

        {/* Water Intake */}
        <div className="mb-6">
          <h3 className="text-sm font-semibold mb-3 text-muted-foreground uppercase tracking-wider">Water Intake</h3>
          <NutritionProgressBar
            name="Water"
            current={nutritionData.water.current}
            target={nutritionData.water.target}
            unit={nutritionData.water.unit}
            color="bg-sky-500"
            icon={<Droplet className="h-4 w-4 text-sky-500" />}
          />
        </div>

        {/* Micronutrients Section */}
        <div className="mb-6">
          <h3 className="text-sm font-semibold mb-3 text-muted-foreground uppercase tracking-wider">Micronutrients</h3>
          {nutritionData.micronutrients.map((micro) => (
            <NutritionProgressBar
              key={micro.name}
              name={micro.name}
              current={micro.current}
              target={micro.target}
              unit={micro.unit}
              color={micro.color}
            />
          ))}
        </div>
      </SidebarContent>
      <SidebarRail side="right" />
    </Sidebar>
  )
}
