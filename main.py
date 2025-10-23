# main.py
from fastapi import FastAPI, HTTPException
from routers import test_api, form_definition_api,  component_definition_api, component_version_api
from routers import form_versions_api
import logging
from logger import setup_logging, get_logger

# Set up logging
setup_logging()
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Form API", version="0.1")

# Register routers
app.include_router(test_api.router)
app.include_router(form_definition_api.router)
app.include_router(component_definition_api.router)
app.include_router(component_version_api.router)  # Added router for component definitions
app.include_router(form_versions_api.router) 

# Middleware for request logging
@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    try:
        response = await call_next(request)
        logger.info(f"Response status: {response.status_code} for {request.method} {request.url}")
        return response
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up the Form API application.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down the Form API application.")
