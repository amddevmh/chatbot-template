from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, Annotated

from app.api.routes import router as api_router
from app.config import settings

app = FastAPI(title="Nutrition Assistant API")

# Configure CORS to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include our API router
app.include_router(api_router, prefix=settings.API_PREFIX)

class ChatMessage(BaseModel):
    message: str

class NutritionRequest(BaseModel):
    message: str

class NutritionResponse(BaseModel):
    id: int
    message: str
    nutrition_data: Optional[Dict[str, Any]] = None

@app.get("/health")
async def health_check():
    """Health check endpoint to verify the API is running"""
    return {"status": "healthy", "message": "API is running"}

@app.post("/api/chat/message")
async def process_chat_message(chat_message: ChatMessage):
    """Process a general chat message"""
    return {
        "message": "I will be in the future changed by AI",
        "processed": True
    }

@app.post("/api/nutrition/extract", response_model=NutritionResponse)
async def extract_nutrition(request: NutritionRequest):
    """Extract nutrition information from user message - currently mocked"""
    # This is a mock response that will be replaced with actual AI processing
    return {
        "id": 1,
        "message": "I will be in the future changed by AI",
        "nutrition_data": {
            "mealName": "Sample Meal",
            "foodItems": [
                {
                    "name": "Sample Food",
                    "calories": 100,
                    "protein": 10,
                    "carbs": 20,
                    "fat": 5
                }
            ]
        }
    }

@app.post("/api/nutrition/confirm/{nutrition_id}")
async def confirm_nutrition(nutrition_id: int):
    """Confirm extracted nutrition information and add to tracker"""
    # Mock confirmation response
    return {
        "message": "I will be in the future changed by AI",
        "confirmed": True,
        "nutrition_id": nutrition_id
    }

@app.post("/api/nutrition/reject/{nutrition_id}")
async def reject_nutrition(nutrition_id: int):
    """Reject extracted nutrition information"""
    # Mock rejection response
    return {
        "message": "I will be in the future changed by AI",
        "rejected": True,
        "nutrition_id": nutrition_id
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
