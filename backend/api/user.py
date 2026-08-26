from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.schemas.user import (
    UserCreateRequest,
    UserResponse,
)
from backend.services.user_service import UserService


router = APIRouter(
    prefix="/api/user",
    tags=["User"],
)


@router.get(
    "",
    response_model=UserResponse | None,
)
async def get_user(
    db: Session = Depends(get_db),
):
    service = UserService(db)

    return service.get_user()


@router.post(
    "",
    response_model=UserResponse,
)
async def save_user(
    request: UserCreateRequest,
    db: Session = Depends(get_db),
):
    try:
        service = UserService(db)

        return service.save_user(
            request.name
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
