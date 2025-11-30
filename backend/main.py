from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.prediction import router as prediction_router
#from routes.health import router as health_router

app = FastAPI(title="Incinerator Site Selection API")

# Register API routes
app.include_router(prediction_router, prefix="/api")

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