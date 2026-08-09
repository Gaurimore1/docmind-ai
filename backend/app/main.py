# main.py
# Entry point for the DocMind AI FastAPI application.
# Creates the app instance and registers all routers.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import upload, search

# FastAPI instance — title and version appear in Swagger UI at /docs.
app = FastAPI(
    title="DocMind AI",
    description="Intelligent Enterprise Document Agent API",
    version="0.1.0",
)

# ---------------------------------------------------------------------------
# CORS — allow the Vite dev server to call the API
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
