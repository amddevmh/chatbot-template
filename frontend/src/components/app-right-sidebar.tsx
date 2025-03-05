import * as React from "react"
import { Apple, Dumbbell, Droplet, Flame, Leaf, Utensils, X, Clock, RefreshCw } from "lucide-react"

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
import { useNutrition, MealItem } from "@/lib/context/nutrition-context"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { 
  Accordion, 
  AccordionContent, 
  AccordionItem, 
  AccordionTrigger 
} from "@/components/ui/accordion"
import { Button } from "@/components/ui/button"

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

// MealCard component for displaying meals with their items
function MealCard({ meal }: { meal: MealItem }) {
  const { removeMeal } = useNutrition();
  const formattedTime = new Date(meal.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  const [expanded, setExpanded] = React.useState(false);
  
  return (
    <Card className="p-3 shadow-sm border border-border/50">
      <div className="flex justify-between items-start">
        <div className="w-full">
          <div className="flex justify-between items-center w-full">
            <h4 className="font-medium text-sm">{meal.name}</h4>
            <Button 
              variant="ghost" 
              size="icon" 
              className="h-6 w-6" 
              onClick={() => removeMeal(meal.id)}
            >
              <X className="h-3 w-3" />
            </Button>
          </div>
          
          <div className="flex items-center mt-1 text-xs text-muted-foreground">
            <Clock className="h-3 w-3 mr-1" />
            <span>{formattedTime}</span>
            <span className="mx-1">•</span>
            <span>{meal.calories} kcal</span>
            <span className="mx-1">•</span>
            <span 
              className="text-primary cursor-pointer hover:underline"
              onClick={() => setExpanded(!expanded)}
            >
              {expanded ? "Hide items" : "Show items"}
            </span>
          </div>
          
          <div className="flex flex-wrap gap-1 mt-1">
            {meal.protein && (
              <Badge variant="secondary" className="text-xs px-1 py-0">
                P: {meal.protein}g
              </Badge>
            )}
            {meal.carbs && (
              <Badge variant="secondary" className="text-xs px-1 py-0">
                C: {meal.carbs}g
              </Badge>
            )}
            {meal.fat && (
              <Badge variant="secondary" className="text-xs px-1 py-0">
                F: {meal.fat}g
              </Badge>
            )}
          </div>
          
          {/* Food items list */}
          {expanded && meal.items && meal.items.length > 0 && (
            <div className="mt-2 border-t pt-2 text-xs">
              <p className="text-muted-foreground mb-1">Items in this meal:</p>
              <ul className="space-y-1 pl-2">
                {meal.items.map((item, index) => (
                  <li key={index} className="flex justify-between">
                    <span>{item.name}</span>
                    <span className="text-muted-foreground">{item.calories} kcal</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </Card>
  );
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
  const { nutritionData, resetNutritionData } = useNutrition()
  const today = new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
  const [resetDialogOpen, setResetDialogOpen] = React.useState(false)
  
  const handleReset = () => {
    resetNutritionData();
    setResetDialogOpen(false);
  }
  
  return (
    <Sidebar side="right" {...props}>
      <SidebarHeader className="h-16 border-b border-sidebar-border">
        <div className="flex items-center justify-between px-4 py-2">
          <h2 className="text-lg font-semibold">Nutrition Tracker</h2>
          <div className="flex items-center gap-2">
            <Dialog open={resetDialogOpen} onOpenChange={setResetDialogOpen}>
              <DialogTrigger asChild>
                <Button variant="ghost" size="icon" className="h-7 w-7" title="Reset nutrition data">
                  <RefreshCw className="h-3.5 w-3.5" />
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Reset Nutrition Data</DialogTitle>
                  <DialogDescription>
                    Are you sure you want to reset all nutrition data? This will clear all logged meals and reset all counters to zero.
                  </DialogDescription>
                </DialogHeader>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setResetDialogOpen(false)}>Cancel</Button>
                  <Button variant="destructive" onClick={handleReset}>Reset Data</Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
            <Badge variant="outline" className="text-xs">
              {today}
            </Badge>
          </div>
        </div>
      </SidebarHeader>
      <SidebarContent className="px-4 py-4">
        {/* Calories Card - Always visible */}
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

        {/* Nutrition Details in Accordion */}
        <Accordion type="multiple" defaultValue={["macros"]} className="w-full">
          {/* Macronutrients Section */}
          <AccordionItem value="macros" className="border-b-0">
            <AccordionTrigger className="py-2 hover:no-underline">
              <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">Macronutrients</h3>
            </AccordionTrigger>
            <AccordionContent>
              <div className="mb-2">
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
            </AccordionContent>
          </AccordionItem>

          <SidebarSeparator className="my-2" />

          {/* Water Intake */}
          <AccordionItem value="water" className="border-b-0">
            <AccordionTrigger className="py-2 hover:no-underline">
              <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">Water Intake</h3>
            </AccordionTrigger>
            <AccordionContent>
              <div className="mb-2">
                <NutritionProgressBar
                  name="Water"
                  current={nutritionData.water.current}
                  target={nutritionData.water.target}
                  unit={nutritionData.water.unit}
                  color="bg-sky-500"
                  icon={<Droplet className="h-4 w-4 text-sky-500" />}
                />
              </div>
            </AccordionContent>
          </AccordionItem>

          <SidebarSeparator className="my-2" />

          {/* Micronutrients Section */}
          <AccordionItem value="micronutrients" className="border-b-0">
            <AccordionTrigger className="py-2 hover:no-underline">
              <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">Micronutrients</h3>
            </AccordionTrigger>
            <AccordionContent>
              <div className="mb-2">
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
            </AccordionContent>
          </AccordionItem>

          <SidebarSeparator className="my-2" />
          
          {/* Logged Meals Section */}
          <AccordionItem value="loggedMeals" className="border-b-0">
            <AccordionTrigger className="py-2 hover:no-underline">
              <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">Logged Meals</h3>
            </AccordionTrigger>
            <AccordionContent>
              <div className="mb-2 space-y-2">
                {nutritionData.loggedMeals.length === 0 ? (
                  <p className="text-sm text-muted-foreground italic">No meals logged today</p>
                ) : (
                  nutritionData.loggedMeals.map((meal) => (
                    <MealCard key={meal.id} meal={meal} />
                  ))
                )}
              </div>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </SidebarContent>
      <SidebarRail side="right" />
    </Sidebar>
  )
}
