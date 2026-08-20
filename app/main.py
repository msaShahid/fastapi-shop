from fastapi import FastAPI

from app.core.config import get_settings
from app.modules.playground.api.router import playground_router

settings = get_settings()

app = FastAPI(
    title="FastAPI Shop",
    version="0.1.0",
    description="A learning project: production-style e-commerce backend.",
)

app.include_router(playground_router, prefix=settings.api_v1_prefix)

@app.get("/health", tags=["health"])
def health_check() -> dict:

    return {
        "status": "ok",
        "environment": settings.environment,
    }


@app.get("/", tags=["Home"])
def home() -> dict:
    return {
        "message": "Welcome to FastAPI Project",
        "app_name": app.title,
        "version": app.version
    }