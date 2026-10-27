"""FastAPI uygulama fabrikası."""
import importlib
import uuid
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import config

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
        allow_origins=config.CORS_ORIGINS,
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    app.include_router(routes_stats.router)
    app.include_router(routes_movies.router)
    app.include_router(routes_recommend.router)
    app.include_router(routes_analysis.router)
    app.include_router(routes_external.router)

    _include_local_routers(app)

    @app.get("/api/health")
    def health():
        return {"status": "ok", "service": "MOVIMIND", "boot_id": BOOT_ID}

    return app


def _include_local_routers(app: FastAPI) -> None:
    """Yalnızca yerelde bulunan router'lar (app/api/local/, .gitignore'da)."""
    local_dir = Path(__file__).resolve().parent / "api" / "local"
    for path in sorted(local_dir.glob("*.py")):
        if path.stem.startswith("_"):
            continue
        module = importlib.import_module(f"app.api.local.{path.stem}")
        app.include_router(module.router)
