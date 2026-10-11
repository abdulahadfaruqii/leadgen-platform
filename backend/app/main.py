"""
FastAPI application entry point.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.db.mongo import close_mongo, connect_mongo
from app.db.session import engine
from app.models import Base

settings = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    configure_logging()
    logger.info("Starting up LeadGen AI Platform")

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Connect MongoDB (optional in local/dev)
    await connect_mongo()

    yield

    # Shutdown
    await close_mongo()
    await engine.dispose()
    logger.info("Shutting down LeadGen AI Platform")


app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise Multi-Agent AI Lead Generation Platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
