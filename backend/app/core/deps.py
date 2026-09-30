from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import resolve_current_user
from app.database.session import get_db
from app.models.user import User
from app.core.config import settings
from app.core.demo_user import get_demo_user_id


async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)) -> User:
    if settings.demo_mode and settings.test_mode and request.cookies.get("studymind_session") is None:
        user_id = await get_demo_user_id(db)
        user = await db.get(User, user_id)
        if user:
            return user
    return await resolve_current_user(request, db)


async def get_current_user_id(request: Request, db: AsyncSession = Depends(get_db)) -> int:
    if settings.demo_mode and settings.test_mode and request.cookies.get("studymind_session") is None:
        return await get_demo_user_id(db)
    user = await resolve_current_user(request, db)
    return user.id
