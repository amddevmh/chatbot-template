from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import Field, validator, BaseModel
from datetime import datetime
from beanie import Document, Link, PydanticObjectId
from uuid import uuid4


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class ActivityLevel(str, Enum):
    SEDENTARY = "sedentary"
    LIGHTLY_ACTIVE = "lightly_active"
    MODERATELY_ACTIVE = "moderately_active"
    VERY_ACTIVE = "very_active"
    EXTREMELY_ACTIVE = "extremely_active"


class NutritionProfile(Document):
    """User's nutrition profile containing general information and preferences"""
    user_id: str = Field(..., description="Unique identifier for the user", index=True)
    age: Optional[int] = Field(None, description="User's age in years", ge=0, le=120)
    gender: Optional[Gender] = Field(None, description="User's gender")
    weight_kg: Optional[float] = Field(None, description="User's weight in kilograms", ge=0)
    height_cm: Optional[float] = Field(None, description="User's height in centimeters", ge=0)
    activity_level: Optional[ActivityLevel] = Field(
        None, 
        description="User's activity level affecting calorie needs"
    )
    daily_calorie_goal: Optional[int] = Field(
        None, 
        description="User's daily calorie goal in kcal",
        ge=0
    )
    macronutrient_goals: Optional[Dict[str, float]] = Field(
        None,
        description="User's macronutrient goals as percentages (protein, carbs, fat)"
    )
    dietary_restrictions: Optional[List[str]] = Field(
        None,
        description="List of dietary restrictions or allergies"
    )
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @validator('macronutrient_goals')
    def validate_macros(cls, v):
        """Validate that macronutrient percentages sum to approximately 100%"""
        if v is None:
            return v
            
        total = sum(v.values())
        if not (99.0 <= total <= 101.0):  # Allow for small rounding errors
            raise ValueError(f"Macronutrient percentages must sum to 100%, got {total}%")
        return v

    def calculate_bmr(self) -> Optional[float]:
        """Calculate Basal Metabolic Rate using the Mifflin-St Jeor Equation"""
        if not all([self.weight_kg, self.height_cm, self.age, self.gender]):
            return None
            
        if self.gender == Gender.MALE:
            return (10 * self.weight_kg) + (6.25 * self.height_cm) - (5 * self.age) + 5
        else:  # Female or other (using female formula as approximation)
            return (10 * self.weight_kg) + (6.25 * self.height_cm) - (5 * self.age) - 161

    def calculate_tdee(self) -> Optional[float]:
        """Calculate Total Daily Energy Expenditure based on BMR and activity level"""
        bmr = self.calculate_bmr()
        if not bmr or not self.activity_level:
            return None
            
        activity_multipliers = {
            ActivityLevel.SEDENTARY: 1.2,
            ActivityLevel.LIGHTLY_ACTIVE: 1.375,
            ActivityLevel.MODERATELY_ACTIVE: 1.55,
            ActivityLevel.VERY_ACTIVE: 1.725,
            ActivityLevel.EXTREMELY_ACTIVE: 1.9
        }
        
        return bmr * activity_multipliers[self.activity_level]


class FoodEntry(BaseModel):
    """Simple food entry structure for meals - will be replaced with RAG later"""
    name: str = Field(..., description="Name of the food item")
    calories: float = Field(..., description="Calories in kcal")
    protein: float = Field(..., description="Protein in grams")
    carbs: float = Field(..., description="Carbohydrates in grams")
    fat: float = Field(..., description="Fat in grams")
    quantity: float = Field(1.0, description="Quantity consumed")
    notes: Optional[str] = Field(None, description="Additional notes about this food entry")
    
    class Config:
        arbitrary_types_allowed = True


class Meal(Document):
    """A meal consisting of multiple food entries"""
    meal_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique identifier for the meal")
    user_id: str = Field(..., description="User who logged this meal", index=True)
    meal_name: str = Field(..., description="Name of the meal (e.g., Breakfast, Lunch)")
    food_entries: List[FoodEntry] = Field(default_factory=list, description="List of food entries in the meal")
    meal_time: datetime = Field(default_factory=datetime.now)
    notes: Optional[str] = Field(None, description="Additional notes about the meal")

    def calculate_meal_totals(self) -> Dict[str, float]:
        """Calculate the total nutrition values for the meal"""
        totals = {
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fat": 0
        }
        
        for entry in self.food_entries:
            totals["calories"] += entry.calories * entry.quantity
            totals["protein"] += entry.protein * entry.quantity
            totals["carbs"] += entry.carbs * entry.quantity
            totals["fat"] += entry.fat * entry.quantity
            
        return totals


class NutritionTracker(Document):
    """Nutrition tracker for recording daily food intake"""
    user_id: str = Field(..., description="User who owns this tracker", index=True)
    date: datetime = Field(default_factory=lambda: datetime.now().date(), index=True)
    meals: List[Meal] = Field(default_factory=list)
    water_intake_ml: Optional[int] = Field(0, description="Water intake in milliliters")
    
    def add_meal(self, meal: Meal) -> None:
        """Add a meal to the tracker"""
        self.meals.append(meal)
    
    def calculate_daily_totals(self) -> Dict[str, float]:
        """Calculate total nutrition values for the day"""
        daily_totals = {
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fat": 0
        }
        
        for meal in self.meals:
            meal_totals = meal.calculate_meal_totals()
            daily_totals["calories"] += meal_totals["calories"]
            daily_totals["protein"] += meal_totals["protein"]
            daily_totals["carbs"] += meal_totals["carbs"]
            daily_totals["fat"] += meal_totals["fat"]
            
        return daily_totals


class NutritionExtraction(Document):
    """Model for nutrition information extracted from user messages"""
    extraction_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique identifier for this extraction", index=True)
    user_id: str = Field(..., description="User who sent the message", index=True)
    original_message: str = Field(..., description="Original message from the user")
    extracted_meal: Optional[Link[Meal]] = Field(None, description="Extracted meal information")
    confidence_score: float = Field(..., description="Confidence score of the extraction", ge=0, le=1)
    status: str = Field("pending", description="Status of the extraction (pending, confirmed, rejected)")
    created_at: datetime = Field(default_factory=datetime.now)
    
    def confirm(self) -> None:
        """Mark the extraction as confirmed"""
        self.status = "confirmed"
    
    def reject(self) -> None:
        """Mark the extraction as rejected"""
        self.status = "rejected"
