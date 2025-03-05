import { createContext, useContext, useState, ReactNode } from "react";

// Meal item type
export interface MealItem {
  id: string;
  name: string;  // This will be the meal name (e.g., "Breakfast", "Lunch")
  calories: number;
  timestamp: string;
  items: {
    name: string;  // Individual food item name
    calories: number;
    protein?: number;
    carbs?: number;
    fat?: number;
    fiber?: number;
  }[];
  protein?: number;
  carbs?: number;
  fat?: number;
  fiber?: number;
  vitaminD?: number;
  iron?: number;
  calcium?: number;
  potassium?: number;
  water?: number;
}

// Nutrition data types
export interface NutritionData {
  calories: {
    current: number;
    target: number;
    unit: string;
  };
  macros: {
    name: string;
    current: number;
    target: number;
    unit: string;
    color: string;
  }[];
  micronutrients: {
    name: string;
    current: number;
    target: number;
    unit: string;
    color: string;
  }[];
  water: {
    current: number;
    target: number;
    unit: string;
  };
  loggedMeals: MealItem[];
}

// Default nutrition data
const defaultNutritionData: NutritionData = {
  calories: {
    current: 0,
    target: 2000,
    unit: "kcal"
  },
  macros: [
    { name: "Protein", current: 0, target: 120, unit: "g", color: "bg-blue-500" },
    { name: "Carbs", current: 0, target: 250, unit: "g", color: "bg-amber-500" },
    { name: "Fat", current: 0, target: 65, unit: "g", color: "bg-rose-500" },
    { name: "Fiber", current: 0, target: 30, unit: "g", color: "bg-green-500" },
  ],
  micronutrients: [
    { name: "Vitamin D", current: 0, target: 15, unit: "μg", color: "bg-yellow-500" },
    { name: "Iron", current: 0, target: 18, unit: "mg", color: "bg-red-500" },
    { name: "Calcium", current: 0, target: 1000, unit: "mg", color: "bg-slate-400" },
    { name: "Potassium", current: 0, target: 3500, unit: "mg", color: "bg-purple-500" },
  ],
  water: {
    current: 0,
    target: 2.5,
    unit: "L"
  },
  loggedMeals: []
};

// Context type
interface NutritionContextType {
  nutritionData: NutritionData;
  updateNutritionData: (newData: Partial<NutritionData>) => void;
  addMeal: (mealName: string, foodItems: {
    name: string;
    calories: number;
    protein?: number;
    carbs?: number;
    fat?: number;
    fiber?: number;
    vitaminD?: number;
    iron?: number;
    calcium?: number;
    potassium?: number;
    water?: number;
  }[]) => void;
  removeMeal: (mealId: string) => void;
  resetNutritionData: () => void;
}

// Create context
const NutritionContext = createContext<NutritionContextType | undefined>(undefined);

// Local storage key
const NUTRITION_STORAGE_KEY = 'nutrition-tracker-data';

// Helper to load data from localStorage
const loadFromLocalStorage = (): NutritionData => {
  if (typeof window === 'undefined') {
    return defaultNutritionData;
  }
  
  try {
    const savedData = localStorage.getItem(NUTRITION_STORAGE_KEY);
    if (savedData) {
      return JSON.parse(savedData) as NutritionData;
    }
  } catch (error) {
    console.error('Error loading nutrition data from localStorage:', error);
  }
  
  return defaultNutritionData;
};

// Helper to save data to localStorage
const saveToLocalStorage = (data: NutritionData) => {
  if (typeof window === 'undefined') {
    return;
  }
  
  try {
    localStorage.setItem(NUTRITION_STORAGE_KEY, JSON.stringify(data));
  } catch (error) {
    console.error('Error saving nutrition data to localStorage:', error);
  }
};

// Provider component
export function NutritionProvider({ children }: { children: ReactNode }) {
  const [nutritionData, setNutritionData] = useState<NutritionData>(() => loadFromLocalStorage());

  // Update nutrition data with partial data
  const updateNutritionData = (newData: Partial<NutritionData>) => {
    setNutritionData(prevData => {
      const updatedData = {
        ...prevData,
        ...newData
      };
      saveToLocalStorage(updatedData);
      return updatedData;
    });
  };

  // Add a meal with multiple food items
  const addMeal = (mealName: string, foodItems: {
    name: string;
    calories: number;
    protein?: number;
    carbs?: number;
    fat?: number;
    fiber?: number;
    vitaminD?: number;
    iron?: number;
    calcium?: number;
    potassium?: number;
    water?: number;
  }[]) => {
    setNutritionData(prevData => {
      // Create a deep copy of the previous data
      const newData = JSON.parse(JSON.stringify(prevData)) as NutritionData;
      
      // Calculate totals for the meal
      let totalCalories = 0;
      let totalProtein = 0;
      let totalCarbs = 0;
      let totalFat = 0;
      let totalFiber = 0;
      let totalVitaminD = 0;
      let totalIron = 0;
      let totalCalcium = 0;
      let totalPotassium = 0;
      let totalWater = 0;
      
      // Sum up all nutrients from all food items
      foodItems.forEach(item => {
        totalCalories += item.calories || 0;
        totalProtein += item.protein || 0;
        totalCarbs += item.carbs || 0;
        totalFat += item.fat || 0;
        totalFiber += item.fiber || 0;
        totalVitaminD += item.vitaminD || 0;
        totalIron += item.iron || 0;
        totalCalcium += item.calcium || 0;
        totalPotassium += item.potassium || 0;
        totalWater += item.water || 0;
      });
      
      // Update calories
      newData.calories.current += totalCalories;
      
      // Update macros
      if (totalProtein) {
        const proteinIndex = newData.macros.findIndex(m => m.name === "Protein");
        if (proteinIndex !== -1) {
          newData.macros[proteinIndex].current += totalProtein;
        }
      }
      
      if (totalCarbs) {
        const carbsIndex = newData.macros.findIndex(m => m.name === "Carbs");
        if (carbsIndex !== -1) {
          newData.macros[carbsIndex].current += totalCarbs;
        }
      }
      
      if (totalFat) {
        const fatIndex = newData.macros.findIndex(m => m.name === "Fat");
        if (fatIndex !== -1) {
          newData.macros[fatIndex].current += totalFat;
        }
      }
      
      if (totalFiber) {
        const fiberIndex = newData.macros.findIndex(m => m.name === "Fiber");
        if (fiberIndex !== -1) {
          newData.macros[fiberIndex].current += totalFiber;
        }
      }
      
      // Update micronutrients
      if (totalVitaminD) {
        const vitaminDIndex = newData.micronutrients.findIndex(m => m.name === "Vitamin D");
        if (vitaminDIndex !== -1) {
          newData.micronutrients[vitaminDIndex].current += totalVitaminD;
        }
      }
      
      if (totalIron) {
        const ironIndex = newData.micronutrients.findIndex(m => m.name === "Iron");
        if (ironIndex !== -1) {
          newData.micronutrients[ironIndex].current += totalIron;
        }
      }
      
      if (totalCalcium) {
        const calciumIndex = newData.micronutrients.findIndex(m => m.name === "Calcium");
        if (calciumIndex !== -1) {
          newData.micronutrients[calciumIndex].current += totalCalcium;
        }
      }
      
      if (totalPotassium) {
        const potassiumIndex = newData.micronutrients.findIndex(m => m.name === "Potassium");
        if (potassiumIndex !== -1) {
          newData.micronutrients[potassiumIndex].current += totalPotassium;
        }
      }
      
      // Update water
      if (totalWater) {
        newData.water.current += totalWater;
      }
      
      // Add to logged meals as a single meal with multiple items
      const newMeal: MealItem = {
        id: Date.now().toString(),
        name: mealName,
        calories: totalCalories,
        timestamp: new Date().toISOString(),
        items: foodItems.map(item => ({
          name: item.name,
          calories: item.calories,
          protein: item.protein,
          carbs: item.carbs,
          fat: item.fat,
          fiber: item.fiber
        })),
        protein: totalProtein,
        carbs: totalCarbs,
        fat: totalFat,
        fiber: totalFiber,
        vitaminD: totalVitaminD,
        iron: totalIron,
        calcium: totalCalcium,
        potassium: totalPotassium,
        water: totalWater
      };
      
      newData.loggedMeals = [newMeal, ...newData.loggedMeals];
      
      saveToLocalStorage(newData);
      return newData;
    });
  };

  // Remove a meal and update nutrition values
  const removeMeal = (mealId: string) => {
    setNutritionData(prevData => {
      // Create a deep copy of the previous data
      const newData = JSON.parse(JSON.stringify(prevData)) as NutritionData;
      
      // Find the meal to remove
      const mealToRemove = newData.loggedMeals.find(meal => meal.id === mealId);
      
      if (!mealToRemove) return newData;
      
      // Update calories
      newData.calories.current -= mealToRemove.calories;
      
      // Update macros
      if (mealToRemove.protein) {
        const proteinIndex = newData.macros.findIndex(m => m.name === "Protein");
        if (proteinIndex !== -1) {
          newData.macros[proteinIndex].current -= mealToRemove.protein;
        }
      }
      
      if (mealToRemove.carbs) {
        const carbsIndex = newData.macros.findIndex(m => m.name === "Carbs");
        if (carbsIndex !== -1) {
          newData.macros[carbsIndex].current -= mealToRemove.carbs;
        }
      }
      
      if (mealToRemove.fat) {
        const fatIndex = newData.macros.findIndex(m => m.name === "Fat");
        if (fatIndex !== -1) {
          newData.macros[fatIndex].current -= mealToRemove.fat;
        }
      }
      
      if (mealToRemove.fiber) {
        const fiberIndex = newData.macros.findIndex(m => m.name === "Fiber");
        if (fiberIndex !== -1) {
          newData.macros[fiberIndex].current -= mealToRemove.fiber;
        }
      }
      
      // Update micronutrients
      if (mealToRemove.vitaminD) {
        const vitaminDIndex = newData.micronutrients.findIndex(m => m.name === "Vitamin D");
        if (vitaminDIndex !== -1) {
          newData.micronutrients[vitaminDIndex].current -= mealToRemove.vitaminD;
        }
      }
      
      if (mealToRemove.iron) {
        const ironIndex = newData.micronutrients.findIndex(m => m.name === "Iron");
        if (ironIndex !== -1) {
          newData.micronutrients[ironIndex].current -= mealToRemove.iron;
        }
      }
      
      if (mealToRemove.calcium) {
        const calciumIndex = newData.micronutrients.findIndex(m => m.name === "Calcium");
        if (calciumIndex !== -1) {
          newData.micronutrients[calciumIndex].current -= mealToRemove.calcium;
        }
      }
      
      if (mealToRemove.potassium) {
        const potassiumIndex = newData.micronutrients.findIndex(m => m.name === "Potassium");
        if (potassiumIndex !== -1) {
          newData.micronutrients[potassiumIndex].current -= mealToRemove.potassium;
        }
      }
      
      // Update water
      if (mealToRemove.water) {
        newData.water.current -= mealToRemove.water;
      }
      
      // Remove from logged meals
      newData.loggedMeals = newData.loggedMeals.filter(meal => meal.id !== mealId);
      
      saveToLocalStorage(newData);
      return newData;
    });
  };

  // Reset nutrition data to defaults
  const resetNutritionData = () => {
    setNutritionData(defaultNutritionData);
    saveToLocalStorage(defaultNutritionData);
  };

  return (
    <NutritionContext.Provider value={{ 
      nutritionData, 
      updateNutritionData, 
      addMeal,
      removeMeal,
      resetNutritionData 
    }}>
      {children}
    </NutritionContext.Provider>
  );
}

// Custom hook to use the nutrition context
export function useNutrition() {
  const context = useContext(NutritionContext);
  if (context === undefined) {
    throw new Error("useNutrition must be used within a NutritionProvider");
  }
  return context;
}
