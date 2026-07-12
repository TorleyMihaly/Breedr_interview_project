

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import measurements, farmers, cows
from app.db import create_db_and_tables


def create_app(*, create_tables: bool = True) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        if create_tables:
            create_db_and_tables()
        yield

    app = FastAPI(
        title="Breedr Project API",
        version="0.1",
        lifespan=lifespan,
    )

    app.include_router(farmers.router, prefix="/farmers", tags=["farmers"])
    app.include_router(cows.router, prefix="/cows", tags=["cows"])
    app.include_router(measurements.router, prefix="/measurements", tags=["measurements"])

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}
    
    return app

app = create_app()
