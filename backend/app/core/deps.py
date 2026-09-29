from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.demo_user import get_demo_user_id
from app.database.session import get_db


async def get_current_user_id(db: AsyncSession = Depends(get_db)) -> int:
    """Demo prototype: always use the deterministic demo learner."""
    return await get_demo_user_id(db)
