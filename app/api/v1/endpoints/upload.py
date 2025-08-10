#!/usr/bin/env python3
"""
🖼️ UPLOAD ENDPOINTS - Shop-Isolated Image Upload API
Provides endpoints for uploading images with shop isolation
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query, Path
from fastapi.responses import JSONResponse
from typing import Optional, List
import os
from pathlib import Path as PathLib

from app.core.deps import get_current_user, require_role, get_current_user_optional
from app.services.image_service import get_image_service, validate_shop
from typing import Dict, Any

router = APIRouter()

@router.post("/upload/{shop}/{category}/")
async def upload_image(
    shop: str = Path(..., description="Shop name: tinashop, micocah, or shared"),
    category: str = Path(..., description="Image category: products, categories, or users"),
    file: UploadFile = File(..., description="Image file to upload"),
    create_thumbnails: bool = Query(True, description="Create thumbnail versions"),
    current_user: Dict[str, Any] = Depends(require_role("admin"))
):
    """
    Upload image with shop isolation
    
    - **shop**: tinashop, micocah, or shared
    - **category**: products, categories, or users  
    - **file**: Image file (JPEG, PNG, WebP, GIF)
    - **create_thumbnails**: Generate different sizes
    
    Requires admin role or higher.
    """
    try:
        # Validate shop
        shop = validate_shop(shop)
        
        # Validate user has access to this shop
        user_shop = current_user.get("shop")
        if user_shop != shop and user_shop != "shared" and current_user.get("role") != "super_admin":
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. You can only upload to {user_shop} shop"
            )
        
        # Get image service for the shop
        image_service = get_image_service(shop)
        
        # Upload image
        result = image_service.upload_image(
            file=file,
            category=category,
            create_thumbnails=create_thumbnails
        )
        
        return {
            "success": True,
            "message": f"Image uploaded successfully to {shop}/{category}",
            "data": result
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/images/{shop}/{category}/")
async def list_images(
    shop: str = Path(..., description="Shop name"),
    category: str = Path(..., description="Image category"),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    """
    List images in a shop category
    
    Public endpoint for viewing images.
    """
    try:
        # Validate shop
        shop = validate_shop(shop)
        
        # Get image service
        image_service = get_image_service(shop)
        
        # List images
        images = image_service.list_images(category)
        
        return {
            "success": True,
            "shop": shop,
            "category": category,
            "total": len(images),
            "images": images
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list images: {str(e)}")

@router.get("/images/{shop}/{category}/{filename}")
async def get_image_info(
    shop: str = Path(..., description="Shop name"),
    category: str = Path(..., description="Image category"),
    filename: str = Path(..., description="Image filename"),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    """
    Get information about specific image
    
    Public endpoint for image metadata.
    """
    try:
        # Validate shop
        shop = validate_shop(shop)
        
        # Get image service
        image_service = get_image_service(shop)
        
        # Get image info
        image_info = image_service.get_image_info(filename, category)
        
        if not image_info:
            raise HTTPException(status_code=404, detail="Image not found")
        
        return {
            "success": True,
            "data": image_info
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get image info: {str(e)}")

@router.delete("/images/{shop}/{category}/{filename}")
async def delete_image(
    shop: str = Path(..., description="Shop name"),
    category: str = Path(..., description="Image category"),
    filename: str = Path(..., description="Image filename"),
    current_user: Dict[str, Any] = Depends(require_role("admin"))
):
    """
    Delete image and its thumbnails
    
    Requires admin role or higher.
    """
    try:
        # Validate shop
        shop = validate_shop(shop)
        
        # Validate user has access to this shop
        user_shop = current_user.get("shop")
        if user_shop != shop and user_shop != "shared" and current_user.get("role") != "super_admin":
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. You can only delete from {user_shop} shop"
            )
        
        # Get image service
        image_service = get_image_service(shop)
        
        # Check if image exists
        image_info = image_service.get_image_info(filename, category)
        if not image_info:
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Delete image
        success = image_service.delete_image(filename, category)
        
        if success:
            return {
                "success": True,
                "message": f"Image {filename} deleted successfully from {shop}/{category}"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to delete image")
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

@router.post("/upload/product-images/{shop}/")
async def upload_product_images(
    shop: str = Path(..., description="Shop name"),
    files: List[UploadFile] = File(..., description="Multiple image files"),
    create_thumbnails: bool = Query(True, description="Create thumbnail versions"),
    current_user: Dict[str, Any] = Depends(require_role("admin"))
):
    """
    Upload multiple product images at once
    
    Batch upload endpoint for efficiency.
    """
    try:
        # Validate shop
        shop = validate_shop(shop)
        
        # Validate user has access to this shop
        user_shop = current_user.get("shop")
        if user_shop != shop and user_shop != "shared" and current_user.get("role") != "super_admin":
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. You can only upload to {user_shop} shop"
            )
        
        # Get image service
        image_service = get_image_service(shop)
        
        # Upload all files
        results = []
        errors = []
        
        for file in files:
            try:
                result = image_service.upload_image(
                    file=file,
                    category="products",
                    create_thumbnails=create_thumbnails
                )
                results.append(result)
            except Exception as e:
                errors.append({
                    "filename": file.filename,
                    "error": str(e)
                })
        
        return {
            "success": True,
            "message": f"Uploaded {len(results)} images to {shop}/products",
            "uploaded": results,
            "errors": errors,
            "total_uploaded": len(results),
            "total_errors": len(errors)
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch upload failed: {str(e)}")

# Health check endpoint
@router.get("/upload/health")
async def upload_health():
    """Health check for upload service"""
    try:
        # Check if static directories exist
        base_path = PathLib("static/images")
        
        status = {
            "status": "healthy",
            "shops": {
                "tinashop": (base_path / "tinashop").exists(),
                "micocah": (base_path / "micocah").exists(),
                "shared": (base_path / "shared").exists()
            },
            "directories_created": True
        }
        
        # Try to create a test service (will create directories)
        try:
            test_service = get_image_service("tinashop")
            status["service_available"] = True
        except Exception as e:
            status["service_available"] = False
            status["error"] = str(e)
        
        return status
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
