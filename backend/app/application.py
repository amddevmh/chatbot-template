#!/usr/bin/env python3
"""
Main application setup for the nutrition assistant
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.api.routes import router as api_router
from app.auth.routes import router as auth_router
from app.auth.middleware import verify_user_middleware
from app.database.mongodb import init_db, close_db_connection
from app.models.user import User
from app.models.nutrition import NutritionProfile, Meal, NutritionTracker


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI
    
    This handles database initialization and cleanup
    """
    # Initialize database connection
    document_models = [
        User,
        NutritionProfile,
        Meal,
        NutritionTracker
    ]
    await init_db(document_models)
    
    yield
    
    # Close database connection
    await close_db_connection()


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application
    
    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title="Nutrition Assistant API",
        description="API for the nutrition assistant application",
        version="0.1.0",
        lifespan=lifespan
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add authentication middleware
    @app.middleware("http")
    async def auth_middleware(request: Request, call_next):
        await verify_user_middleware(request)
        return await call_next(request)
    
    # Include routers
    app.include_router(
        auth_router,
        prefix=f"{settings.API_PREFIX}/auth",
        tags=["Authentication"]
    )
    
    app.include_router(
        api_router,
        prefix=settings.API_PREFIX,
        tags=["API"]
    )
    
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint to verify the API is running"""
        return {"status": "healthy", "message": "API is running"}
    
    return app


# Create the application instance
app = create_application()
