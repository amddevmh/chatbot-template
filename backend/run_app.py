#!/usr/bin/env python3
"""
Run the FastAPI application for testing
"""
import uvicorn
import sys
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("run_app")

if __name__ == "__main__":
    try:
        # Add logging for startup process
        logger.info("Starting FastAPI server...")
        
        # Import the app first to test if it can be loaded
        logger.info("Importing app module...")
        from app.application import app
        logger.info("App module imported successfully")
        
        # Log the setup before running
        logger.info("Running uvicorn server")
        uvicorn.run("app.application:app", host="127.0.0.1", port=8000, reload=False, log_level="debug")
    except Exception as e:
        error_detail = f"Error starting server: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_detail)
        print(error_detail, file=sys.stderr)
        sys.exit(1)
