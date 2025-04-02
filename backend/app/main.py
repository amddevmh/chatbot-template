#!/usr/bin/env python3
"""
Main entry point for the chatbot backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
from app.auth.routes import router as auth_router
from app.config import settings

app = FastAPI(title=settings.APP_NAME)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Auth routes
app.include_router(auth_router, prefix=f"{settings.API_PREFIX}/auth", tags=["Authentication"])

# Include API routes
app.include_router(api_router, prefix=settings.API_PREFIX, tags=["API"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)