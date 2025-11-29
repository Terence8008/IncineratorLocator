from fastapi import FastAPI
from routes.prediction import router as prediction_router
#from routes.health import router as health_router

app = FastAPI(title="Incinerator Site Selection API")

# Register API routes
app.include_router(prediction_router, prefix="/api")
