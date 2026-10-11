"""
Database seed script for development.
"""
import asyncio
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.core.security import get_password_hash


async def seed():
    async with AsyncSessionLocal() as db:
        # Create admin user
        admin = User(
            email="admin@leadgen.ai",
            hashed_password=get_password_hash("admin123"),
            full_name="Admin User",
            is_superuser=True,
            is_verified=True,
            subscription_tier="enterprise",
        )
        db.add(admin)
        await db.commit()
        print("Admin user created: admin@leadgen.ai / admin123")


if __name__ == "__main__":
    asyncio.run(seed())
