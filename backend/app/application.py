#!/usr/bin/env python3
"""
Main application setup for the FastAPI starter template
"""
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.models import SecuritySchemeType
from contextlib import asynccontextmanager
import logging
import traceback
import sys

from app.config import settings
from app.api.routes import router as api_router
from app.auth.routes import router as auth_router
from app.database.mongodb import init_db, close_db_connection
from app.models.user import User
from app.models.chat_session import ChatSessionMetadata

# Set up logging - this is the ONLY place where basicConfig should be called
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("app.application")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI
    
    This handles database initialization and cleanup
    """
    try:
        logger.info("Starting application lifespan manager")
        # Initialize database connection
        document_models = [
            User,
            ChatSessionMetadata
            # Add more document models here as needed
        ]
        logger.info(f"Initializing database with models: {document_models}")
        await init_db(document_models)
        logger.info("Database initialization completed successfully")
        
        # Log application startup status
        logger.info("Application startup successful, ready to handle requests")
        
        yield
    except Exception as e:
        logger.error(f"Error during application startup: {str(e)}")
        logger.error(traceback.format_exc())
        # We still yield to allow FastAPI to handle the error appropriately
        yield
    finally:    
        # Close database connection
        logger.info("Shutting down application, closing database connection")
        try:
            await close_db_connection()
            logger.info("Database connection closed successfully")
        except Exception as e:
            logger.error(f"Error closing database connection: {str(e)}")


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application
    
    Returns:
        Configured FastAPI application
    """
    logger.info("Creating FastAPI application")
    app = FastAPI(
        title="FastAPI Starter Template",
        description="A production-ready FastAPI starter template with MongoDB integration and JWT authentication",
        version="1.0.0",
        lifespan=lifespan,
        # Define tags for API documentation
        openapi_tags=[
            {"name": "Authentication", "description": "Authentication endpoints"},
            {"name": "API", "description": "API endpoints"},
            {"name": "Health", "description": "Health check endpoint"}
        ],
        swagger_ui_parameters={"persistAuthorization": True}
    )
    
    # Add security definitions for Swagger UI
    app.swagger_ui_init_oauth = {
        "usePkceWithAuthorizationCodeGrant": True
    }
    
    # Define the apiKey security scheme for Bearer token
    app.openapi_components = {
        "securitySchemes": {
            "apikey": {
                "type": "apiKey",
                "in": "header",
                "name": "Authorization",
                "description": "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the token"
            }
        }
    }
    
    # Apply security globally to all endpoints
    app.openapi_security = [{"apikey": []}]
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    
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
        try:
            logger.info("Health check endpoint called")
            return {"status": "healthy", "message": "API is running"}
        except Exception as e:
            logger.error(f"Error in health check: {str(e)}")
            logger.error(traceback.format_exc())
            # Return status code 200 with error details to help with debugging
            return {"status": "error", "message": str(e), "traceback": traceback.format_exc()}
    
    return app


# Create the application instance
try:
    logger.info("Initializing application instance")
    app = create_application()
    logger.info("Application instance created successfully")
except Exception as e:
    logger.critical(f"Failed to create application instance: {str(e)}")
    logger.critical(traceback.format_exc())
    # Re-raise to prevent app startup
    raise
