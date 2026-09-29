from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user_id
from app.database.session import get_db
from app.services.recommendation_service import recommendation_service

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/next-action")
async def get_next_best_action(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await recommendation_service.get_next_best_action(user_id, db)
