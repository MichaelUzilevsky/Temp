from contextlib import asynccontextmanager
from typing import cast, AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.exceptions.handlers import domain_exception_handler, unhandled_exception_handler
from app.api.v1.endpoints import resources, operators, missions
from app.db.sql.manager import SQLAlchemyManager
from app.domain.exceptions.domain_exception import DomainException


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    # Initialize manager
    app.state.db_manager = SQLAlchemyManager

    yield

    # Cleanup
    # await app.state.db_manager.close()


class AppFactory:
    @staticmethod
    def create_app() -> FastAPI:
        app = FastAPI(title="Live Missions API", version="1.0.0", lifespan=lifespan)

        app.add_middleware(
            cast("_MiddlewareFactory", CORSMiddleware),
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Register global exception handlers
        app.add_exception_handler(DomainException, domain_exception_handler)
        app.add_exception_handler(Exception, unhandled_exception_handler)

        # Include versioned routes
        app.include_router(resources.router, prefix="/api/v1")
        app.include_router(operators.router, prefix="/api/v1")
        app.include_router(missions.router, prefix="/api/v1")

        return app
