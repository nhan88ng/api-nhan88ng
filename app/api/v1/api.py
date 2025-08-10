from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, products, upload

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(upload.router, prefix="/upload", tags=["image-upload"])
