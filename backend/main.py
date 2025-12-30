from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from routes.prediction import router as prediction_router
from routes.layers import router as layer_router
#from routes.health import router as health_router

app = FastAPI(title="Incinerator Site Selection API")

# Mount the processed data folder so frontend can access the .png plots
# Access via: http://localhost:8000/static/confusion_matrix.png
DATA_PATH = Path(__file__).resolve().parent.parent / "backend"/ "static"/ "metrics"
app.mount("/static", StaticFiles(directory=DATA_PATH), name="static")

# Register API routes
app.include_router(prediction_router, prefix="/api")
app.include_router(layer_router, prefix="/api")

# Allow CORS
origins = [
    "http://localhost:3000",  # your React app
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # allow all HTTP methods
    allow_headers=["*"],  # allow all headers
)