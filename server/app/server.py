"""FastAPI uygulama fabrikası."""
import uuid

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

BOOT_ID = str(uuid.uuid4())

from app.api import (
    routes_analysis,
    routes_external,
    routes_movies,
    routes_recommend,
    routes_stats,
)


def create_app() -> FastAPI:
    app = FastAPI(title="MOVIMIND API", version="1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    app.include_router(routes_stats.router)
    app.include_router(routes_movies.router)
    app.include_router(routes_recommend.router)
    app.include_router(routes_analysis.router)
    app.include_router(routes_external.router)

    @app.get("/api/health")
    def health():
        return {"status": "ok", "service": "MOVIMIND", "boot_id": BOOT_ID}

    return app
