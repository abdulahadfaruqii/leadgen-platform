"""
MongoDB connection for unstructured data and analytics.
"""
from app.core.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)

mongo_client = None

try:
    from motor.motor_asyncio import AsyncIOMotorClient
    from pymongo import ASCENDING

    MOTOR_AVAILABLE = True
except ImportError:
    AsyncIOMotorClient = None  # type: ignore
    ASCENDING = None  # type: ignore
    MOTOR_AVAILABLE = False


async def connect_mongo() -> None:
    global mongo_client
    if not settings.MONGO_ENABLED:
        logger.warning("MongoDB disabled — skipping connection")
        return

    if not MOTOR_AVAILABLE:
        logger.warning("motor/pymongo not installed — skipping MongoDB")
        return

    try:
        mongo_client = AsyncIOMotorClient(
            settings.MONGO_URL,
            serverSelectionTimeoutMS=2000,
        )
        await mongo_client.admin.command("ping")
        logger.info("MongoDB connected")

        db = mongo_client[settings.MONGO_DB]
        await db.analytics_events.create_index([("timestamp", ASCENDING)])
        await db.analytics_events.create_index([("event_type", ASCENDING)])
        await db.analytics_events.create_index([("campaign_id", ASCENDING)])
        await db.scraped_content.create_index([("business_id", ASCENDING)])
        await db.scraped_content.create_index([("url", ASCENDING)])
    except Exception as exc:
        logger.warning("MongoDB unavailable — continuing without it: %s", exc)
        mongo_client = None


async def close_mongo() -> None:
    global mongo_client
    if mongo_client:
        mongo_client.close()
        logger.info("MongoDB disconnected")


def get_mongo_db():
    if mongo_client is None:
        raise RuntimeError("MongoDB is not connected")
    return mongo_client[settings.MONGO_DB]
