# main.py
# Entry point for the DocMind AI FastAPI application.
# Creates the app instance and registers all routers.

from fastapi import FastAPI
from app.routers import upload, search

# FastAPI instance — title and version appear in Swagger UI at /docs.
app = FastAPI(
    title="DocMind AI",
    description="Intelligent Enterprise Document Agent API",
    version="0.1.0",
)

# Register the upload router.
# All routes in upload.py are prefixed with /api/v1.
# Final upload URL: POST /api/v1/upload
app.include_router(upload.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")


# Root health-check — confirms the server is running.
@app.get("/")
def home():
    return {"message": "Welcome to DocMind AI"}
