from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import get_settings
from backend.routes import router


settings = get_settings()


app = FastAPI(

    title=settings.app_name,

    version="1.0.0",

    description=(
        "AI-powered legal document "
        "drafting backend."
    )
)


app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=False,

    allow_methods=[
        "GET",
        "POST"
    ],

    allow_headers=["*"]
)


app.include_router(router)


@app.get(
    "/",
    tags=["health"]
)
def root():

    return {

        "app": settings.app_name,

        "status": "running",

        "docs": "/docs"
    }


@app.get(
    "/health",
    tags=["health"]
)
def health():

    return {

        "status": "ok",

        "gemini_configured": bool(
            settings.gemini_api_key
        ),

        "model": settings.gemini_model
    }

