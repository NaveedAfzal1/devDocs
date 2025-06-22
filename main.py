import time
from datetime import datetime, timezone
from fastapi import FastAPI, Request, HTTPException
from starlette.responses import JSONResponse
from routers import projects, issues, resolutions
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Backend Issue Tracker API",
    description="A robust API for tracking issues and resolutions for software projects.",
    version="2.0.0"
)

# 5. Add Request Logging Middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        f"Request: {request.method} {request.url} | Status Code: {response.status_code} | Execution Time: {process_time:.4f}s"
    )
    return response

# 8. Add a Health Check Endpoint
@app.get("/health", tags=["Health"])
def health_check():
    """
    Checks the operational status of the API.
    """
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# Include routers
app.include_router(projects.router, prefix="/projects", tags=["Projects"])
app.include_router(issues.router, prefix="/issues", tags=["Issues"])
app.include_router(resolutions.router, prefix="/resolutions", tags=["Resolutions"])

# Generic error handling to catch unhandled exceptions
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception for {request.method} {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected server error occurred."},
    )