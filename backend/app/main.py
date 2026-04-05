from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import traceback
from contextlib import asynccontextmanager

# Import database initialization and models
from app.database import init_db, close_db, Base, engine
# Import all models so they are registered with SQLAlchemy
from app.models.db_models import Sensor, SensorReading, Alert

from app.routers.sensors_router import router as sensors_router
from app.routers.history_router import router as history_router
from app.routers.alerts_router import router as alerts_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle context manager.
    Handles startup and shutdown events.
    """
    # Startup
    print("🚀 Application starting...")
    await init_db()
    yield
    # Shutdown
    print("🛑 Application shutting down...")
    await close_db()


app = FastAPI(
    title="Sensor Visualization API",
    description="Real-time sensor data visualization and monitoring",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "API is running"}


# CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, use specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global Exception Handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    print("❌ Server error:", traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )


# Include routers
app.include_router(sensors_router, prefix="/api", tags=["sensors"])
app.include_router(history_router, prefix="/api", tags=["history"])
app.include_router(alerts_router, prefix="/api", tags=["alerts"])


# Root endpoint
@app.get("/")
def root():
    """API root endpoint with documentation links."""
    return {
        "message": "Welcome to Sensor Visualization API",
        "docs": "/docs",
        "health": "/health"
    }
