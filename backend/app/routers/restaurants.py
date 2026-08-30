"""
GET /restaurants/{restaurant_id} — full restaurant detail with menu items.

Used by the restaurant detail screen (Person 1's frontend).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.restaurant import Restaurant
from app.schemas.restaurant import RestaurantDetail

router = APIRouter()


@router.get(
    "/{restaurant_id}",
    response_model=RestaurantDetail,
    summary="Get restaurant detail",
    description=(
        "Returns full restaurant info including all menu items. "
        "Called when the user taps a feed card to open the detail screen."
    ),
)
async def get_restaurant(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db),
) -> RestaurantDetail:
    stmt = (
        select(Restaurant)
        .options(selectinload(Restaurant.items))
        .where(Restaurant.restaurant_id == restaurant_id)
    )
    result = await db.execute(stmt)
    restaurant = result.scalar_one_or_none()

    if restaurant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Restaurant '{restaurant_id}' not found.",
        )

    return RestaurantDetail.model_validate(restaurant)