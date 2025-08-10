from fastapi import APIRouter, HTTPException
from typing import List

router = APIRouter()

@router.get("/")
async def get_users():
    return {"message": "Get all users - to be implemented"}

@router.get("/{user_id}")
async def get_user(user_id: str):
    return {"message": f"Get user {user_id} - to be implemented"}

@router.put("/{user_id}")
async def update_user(user_id: str):
    return {"message": f"Update user {user_id} - to be implemented"}

@router.delete("/{user_id}")
async def delete_user(user_id: str):
    return {"message": f"Delete user {user_id} - to be implemented"}
