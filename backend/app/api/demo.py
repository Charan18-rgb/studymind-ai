from fastapi import APIRouter, Depends, HTTPException
from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.demo_data import create_demo_data, reset_demo_data
from app.database.session import get_db
from app.core.deps import get_current_user_id
from app.models.user import User
from sqlalchemy import select

router = APIRouter(prefix="/demo", tags=["demo"])


@router.post("/initialize")
async def initialize_demo_data(user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    if not settings.demo_mode:
        raise HTTPException(status_code=404, detail="Not found")
    user = await db.scalar(select(User).where(User.id == user_id))
    if not user or not user.is_demo and not settings.test_mode:
        raise HTTPException(status_code=404, detail="Not found")
    return await create_demo_data(db)


@router.post("/reset")
async def reset_demo(user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    if not settings.demo_mode:
        raise HTTPException(status_code=404, detail="Not found")
    user = await db.scalar(select(User).where(User.id == user_id))
    if not user or not user.is_demo and not settings.test_mode:
        raise HTTPException(status_code=404, detail="Not found")
    return await reset_demo_data(db)
