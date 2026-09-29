"""Deterministic demo user — single source of truth for hackathon demo mode."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User

DEMO_USER_EMAIL = "demo@studymind.ai"
DEMO_USER_NAME = "Demo Student"


async def get_or_create_demo_user(db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.email == DEMO_USER_EMAIL))
    user = result.scalar_one_or_none()
    if user:
        return user
    user = User(email=DEMO_USER_EMAIL, name=DEMO_USER_NAME, is_demo=True)
    db.add(user)
    await db.flush()
    return user


async def get_demo_user_id(db: AsyncSession) -> int:
    user = await get_or_create_demo_user(db)
    return user.id
