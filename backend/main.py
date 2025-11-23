from fastapi import FastAPI
from prediction import router as prediction_router
from .routes.describe import router as describe_router
from .routes.health import router as health_router

app = FastAPI(title="Incinerator Site Selection API")

# Register API routes
app.include_router(prediction_router, prefix="/api")
app.include_router(describe_router, prefix="/api")
app.include_router(health_router, prefix="/api")
