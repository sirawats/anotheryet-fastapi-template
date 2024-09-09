from typing import List

from app.api.v1.users import schema
from app.api.v1.users.service import UserService
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(prefix="/users", tags=["users"])



@router.get("/", response_model=List[schema.User])
async def get_users(skip: int = 0, limit: int = 100, user_service: UserService = Depends()):
    return await user_service.get_all(skip=skip, limit=limit)


@router.get("/{user_id}", response_model=schema.User)
async def get_user(user_id: int, user_service: UserService = Depends()):
    user = await user_service.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=schema.User)
async def create_user(user_create: schema.UserCreate, user_service: UserService = Depends()):
    return await user_service.create(user_create)


@router.put("/{user_id}", response_model=schema.User)
async def update_user(user_id: int, user_update: schema.UserUpdate, user_service: UserService = Depends()):
    try:
        return await user_service.update(user_id, user_update)
    except ValueError:
        raise HTTPException(status_code=404, detail="User not found")


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, user_service: UserService = Depends()):
    try:
        await user_service.delete(user_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="User not found")
