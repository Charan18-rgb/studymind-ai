from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.demo_data import create_demo_data, reset_demo_data
from app.database.session import get_db

router = APIRouter(prefix="/demo", tags=["demo"])


@router.post("/initialize")
async def initialize_demo_data(db: AsyncSession = Depends(get_db)):
    return await create_demo_data(db)


@router.post("/reset")
async def reset_demo(db: AsyncSession = Depends(get_db)):
    return await reset_demo_data(db)
