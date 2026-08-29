"""
Main FastAPI application entry point.
Run with: uvicorn backend.app.main:app --reload
"""

from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.routes import router


# ─────────────────────────────────────────────
# APPLICATION FACTORY
# ─────────────────────────────────────────────

def create_app() -> FastAPI:
    application = FastAPI(
        title="AI Career & College Intelligence Platform",
        description=(
            "An intelligent platform that provides multi-factor college recommendations, "
            "career roadmaps, skill gap analysis, and personalized guidance for students "
            "based on their academic profile, interests, and goals."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        contact={
            "name": "AI Career Platform",
            "email": "support@aicareer.dev",
        },
    )

    # ── CORS Middleware ──────────────────────────────────────────────────────
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",  # Vite dev server
            "http://localhost:3000",  # Alternative dev port
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Register Routers ─────────────────────────────────────────────────────
    application.include_router(router, prefix="/api/v1", tags=["Career Intelligence"])

    return application


app = create_app()


# ─────────────────────────────────────────────
# ROOT REDIRECT
# ─────────────────────────────────────────────

@app.get("/", include_in_schema=False)
def root() -> dict:
    return {
        "message": "AI Career & College Intelligence Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }
