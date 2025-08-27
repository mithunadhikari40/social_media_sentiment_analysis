from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models, auth, routes
from .database import engine

# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Social Media Sentiment Analysis API",
    description="An API to analyze sentiment from social media data and generate reports.",
    version="1.0.0",
    debug=True
)

# List of allowed origins (e.g., React frontend URL, localhost, etc.)
origins = [
    "http://127.0.0.1:3000", # React dev server
    "http://localhost:5173",   # Vite dev server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # list of allowed origins
    allow_credentials=True,         # whether to allow cookies/authorization headers
    allow_methods=["*"],            # allow all HTTP methods
    allow_headers=["*"],            # allow all headers
)

# Include the authentication router
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Include the analysis router
app.include_router(routes.router, prefix="/api", tags=["Analysis"])

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Sentiment Analysis API. Visit /docs for documentation."}
