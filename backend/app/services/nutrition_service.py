from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from beanie import PydanticObjectId
from app.models.nutrition import (
    NutritionProfile, 
    FoodEntry, 
    Meal, 
    NutritionTracker,
    NutritionExtraction
)


class NutritionService:
    @staticmethod
    async def create_or_update_profile(user_id: str, profile_data: Dict[str, Any]) -> NutritionProfile:
        """Create or update a user's nutrition profile"""
        # Check if profile exists
        profile = await NutritionProfile.find_one({"user_id": user_id})
        
        if profile:
            # Update existing profile
            for key, value in profile_data.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
            profile.updated_at = datetime.now()
            await profile.save()
        else:
            # Create new profile
            profile_data["user_id"] = user_id
            profile = NutritionProfile(**profile_data)
            await profile.insert()
            
        return profile
    
    @staticmethod
    async def get_profile(user_id: str) -> Optional[NutritionProfile]:
        """Get a user's nutrition profile"""
        return await NutritionProfile.find_one({"user_id": user_id})
    
    @staticmethod
    async def extract_nutrition_from_message(user_id: str, message: str) -> NutritionExtraction:
        """
        Extract nutrition information from a user message
        In a real application, this would use an AI model to extract the information
        """
        # Mock extraction for demonstration purposes
        
        # This is where AI would analyze the message and extract food items
        # For now, we'll create a mock meal with mock food entries
        food_entry = FoodEntry(
            name="Sample Food",
            calories=100,
            protein=10,
            carbs=20,
            fat=5,
            quantity=1.0,
            notes="Sample food entry"
        )
        
        meal = Meal(
            user_id=user_id,
            meal_name="Sample Meal",
            food_entries=[food_entry],
            meal_time=datetime.now()
        )
        await meal.insert()
        
        extraction = NutritionExtraction(
            user_id=user_id,
            original_message=message,
            extracted_meal=meal,
            confidence_score=0.85,
            status="pending"
        )
        
        await extraction.insert()
        return extraction
    
    @staticmethod
    async def confirm_extraction(extraction_id: str) -> Tuple[bool, Optional[NutritionExtraction]]:
        """Confirm a nutrition extraction and add it to the user's tracker"""
        extraction = await NutritionExtraction.find_one({"extraction_id": extraction_id})
        if not extraction:
            return False, None
            
        if extraction.status != "pending":
            return False, extraction
            
        extraction.confirm()
        await extraction.save()
        
        # Add the meal to the user's tracker
        if extraction.extracted_meal:
            user_id = extraction.user_id
            date = extraction.created_at.date()
            
            # Find or create tracker for this date
            tracker = await NutritionTracker.find_one({
                "user_id": user_id,
                "date": {"$gte": datetime(date.year, date.month, date.day, 0, 0, 0),
                         "$lt": datetime(date.year, date.month, date.day, 23, 59, 59)}
            })
            
            if not tracker:
                tracker = NutritionTracker(user_id=user_id, date=date)
                await tracker.insert()
            
            # Add the meal to the tracker
            meal = await extraction.extracted_meal.fetch()
            tracker.meals.append(meal)
            await tracker.save()
            
        return True, extraction
    
    @staticmethod
    async def reject_extraction(extraction_id: str) -> Tuple[bool, Optional[NutritionExtraction]]:
        """Reject a nutrition extraction"""
        extraction = await NutritionExtraction.find_one({"extraction_id": extraction_id})
        if not extraction:
            return False, None
            
        if extraction.status != "pending":
            return False, extraction
            
        extraction.reject()
        await extraction.save()
        return True, extraction
    
    @staticmethod
    async def get_extraction(extraction_id: str) -> Optional[NutritionExtraction]:
        """Get a nutrition extraction by ID"""
        return await NutritionExtraction.find_one({"extraction_id": extraction_id})
    
    @staticmethod
    async def get_or_create_tracker(user_id: str, date: Optional[datetime] = None) -> NutritionTracker:
        """Get or create a user's daily nutrition tracker"""
        return await NutritionService.get_daily_tracker(user_id, date)
        
    @staticmethod
    async def get_daily_tracker(user_id: str, date: Optional[datetime] = None) -> NutritionTracker:
        """Get a user's daily nutrition tracker"""
        if date is None:
            date = datetime.now()
        
        date_obj = date.date()
        
        # Find tracker for this date
        tracker = await NutritionTracker.find_one({
            "user_id": user_id,
            "date": {"$gte": datetime(date_obj.year, date_obj.month, date_obj.day, 0, 0, 0),
                     "$lt": datetime(date_obj.year, date_obj.month, date_obj.day, 23, 59, 59)}
        })
        
        if not tracker:
            tracker = NutritionTracker(user_id=user_id, date=date)
            await tracker.insert()
        
        return tracker
