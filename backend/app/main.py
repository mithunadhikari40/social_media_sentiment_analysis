from fastapi import FastAPI
from . import models, auth, routes
from .database import engine

# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Social Media Sentiment Analysis API",
    description="An API to analyze sentiment from social media data and generate reports.",
    version="1.0.0"
)

# Include the authentication router
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Include the analysis router
app.include_router(routes.router, prefix="/api", tags=["Analysis"])

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Sentiment Analysis API. Visit /docs for documentation."}
