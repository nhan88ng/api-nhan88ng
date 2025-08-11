"""
Shop API Routes
FastAPI endpoints for shop management and information
"""

from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends

from app.core.shop_manager import get_shop_manager, ShopConfig
from app.core.deps import get_current_user_optional

router = APIRouter()

@router.get("/", response_model=Dict[str, Any])
async def get_all_shops(
    current_user: dict = Depends(get_current_user_optional)
):
    """
    Get all available shops with basic information
    
    **Authentication optional**
    """
    shop_manager = get_shop_manager()
    shops = shop_manager.get_all_shops()
    
    # Return shop info without sensitive data
    shops_info = {}
    for shop_id, config in shops.items():
        shops_info[shop_id] = {
            "id": config.id,
            "name": config.name,
            "description": config.description,
            "domain": config.domain,
            "frontend_url": config.frontend_url,
            "theme": {
                "primary_color": config.theme.primary_color,
                "secondary_color": config.theme.secondary_color,
                "logo": config.theme.logo
            },
            "features": config.features,
            "settings": {
                "currency": config.settings.currency,
                "language": config.settings.language,
                "allow_guest_checkout": config.settings.allow_guest_checkout,
                "enable_reviews": config.settings.enable_reviews,
                "enable_wishlist": config.settings.enable_wishlist
            },
            "contact": {
                "email": config.contact.email,
                "phone": config.contact.phone,
                "address": config.contact.address
            },
            "social": config.social
        }
    
    return {
        "total_shops": len(shops_info),
        "shops": shops_info
    }

@router.get("/{shop_id}", response_model=Dict[str, Any])
async def get_shop_info(
    shop_id: str,
    current_user: dict = Depends(get_current_user_optional)
):
    """
    Get detailed information about a specific shop
    
    **Authentication optional**
    """
    shop_manager = get_shop_manager()
    shop_config = shop_manager.get_shop(shop_id)
    
    if not shop_config:
        available_shops = shop_manager.get_shop_ids()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shop '{shop_id}' not found. Available shops: {available_shops}"
        )
    
    # Return detailed shop info without sensitive data
    return {
        "id": shop_config.id,
        "name": shop_config.name,
        "description": shop_config.description,
        "domain": shop_config.domain,
        "frontend_url": shop_config.frontend_url,
        "theme": {
            "primary_color": shop_config.theme.primary_color,
            "secondary_color": shop_config.theme.secondary_color,
            "logo": shop_config.theme.logo,
            "favicon": shop_config.theme.favicon,
            "banner": shop_config.theme.banner
        },
        "features": shop_config.features,
        "settings": {
            "currency": shop_config.settings.currency,
            "language": shop_config.settings.language,
            "timezone": shop_config.settings.timezone,
            "allow_guest_checkout": shop_config.settings.allow_guest_checkout,
            "require_email_verification": shop_config.settings.require_email_verification,
            "enable_reviews": shop_config.settings.enable_reviews,
            "enable_wishlist": shop_config.settings.enable_wishlist
        },
        "contact": {
            "email": shop_config.contact.email,
            "phone": shop_config.contact.phone,
            "address": shop_config.contact.address
        },
        "social": shop_config.social
    }

@router.get("/{shop_id}/features", response_model=List[str])
async def get_shop_features(
    shop_id: str,
    current_user: dict = Depends(get_current_user_optional)
):
    """
    Get enabled features for a specific shop
    
    **Authentication optional**
    """
    shop_manager = get_shop_manager()
    
    if not shop_manager.is_valid_shop(shop_id):
        available_shops = shop_manager.get_shop_ids()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shop '{shop_id}' not found. Available shops: {available_shops}"
        )
    
    return shop_manager.get_shop_features(shop_id)
