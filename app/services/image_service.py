#!/usr/bin/env python3
"""
🖼️ IMAGE SERVICE - Shop-Isolated Image Management
Handles image upload, processing, and serving with shop isolation
"""

import os
import uuid
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any
from PIL import Image, ImageOps
from fastapi import UploadFile, HTTPException
import mimetypes

class ImageService:
    """Service for handling shop-isolated image operations"""
    
    # Allowed image types
    ALLOWED_TYPES = {
        'image/jpeg', 'image/jpg', 'image/png', 
        'image/webp', 'image/gif'
    }
    
    # Max file size (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    # Image sizes for different purposes
    IMAGE_SIZES = {
        'thumbnail': (150, 150),
        'small': (300, 300),
        'medium': (600, 600),
        'large': (1200, 1200)
    }
    
    def __init__(self, shop: str):
        """Initialize service for specific shop"""
        # Validate shop
        if shop not in ['tinashop', 'micocah', 'shared']:
            raise ValueError(f"Invalid shop: {shop}. Must be 'tinashop', 'micocah', or 'shared'")
        
        self.shop = shop
        self.base_path = Path("static") / "images" / shop
        self.base_url = f"/static/images/{shop}"
        
        # Ensure directories exist
        self._create_directories()
    
    def _create_directories(self):
        """Create necessary directories for the shop"""
        directories = ['products', 'categories', 'users', 'temp']
        
        for directory in directories:
            dir_path = self.base_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def _validate_file(self, file: UploadFile) -> None:
        """Validate uploaded file"""
        # Check content type
        if file.content_type not in self.ALLOWED_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type: {file.content_type}. Allowed: {', '.join(self.ALLOWED_TYPES)}"
            )
        
        # Check file size (read and reset position)
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        if file_size > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large: {file_size} bytes. Max allowed: {self.MAX_FILE_SIZE} bytes"
            )
        
        # Validate filename
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
    
    def _generate_filename(self, original_filename: str) -> str:
        """Generate unique filename"""
        file_extension = Path(original_filename).suffix.lower()
        if not file_extension:
            file_extension = '.jpg'  # Default extension
        
        unique_id = str(uuid.uuid4())
        return f"{unique_id}{file_extension}"
    
    def _save_file(self, file: UploadFile, file_path: Path) -> None:
        """Save uploaded file to disk"""
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save file: {str(e)}"
            )
    
    def _create_thumbnails(self, source_path: Path, category: str, filename_base: str) -> Dict[str, str]:
        """Create different sized thumbnails"""
        thumbnails = {}
        
        try:
            with Image.open(source_path) as img:
                # Convert to RGB if necessary (for JPEG)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                # Create thumbnails for each size
                for size_name, (width, height) in self.IMAGE_SIZES.items():
                    # Skip if original is smaller than thumbnail size
                    if img.width <= width and img.height <= height and size_name != 'thumbnail':
                        continue
                    
                    # Create thumbnail
                    thumb = img.copy()
                    thumb.thumbnail((width, height), Image.Resampling.LANCZOS)
                    
                    # Save thumbnail
                    thumb_filename = f"{filename_base}_{size_name}.jpg"
                    thumb_path = self.base_path / category / thumb_filename
                    thumb.save(thumb_path, "JPEG", quality=85, optimize=True)
                    
                    # Store URL
                    thumbnails[size_name] = f"{self.base_url}/{category}/{thumb_filename}"
        
        except Exception as e:
            print(f"Warning: Failed to create thumbnails: {str(e)}")
            # Don't fail the upload if thumbnail creation fails
        
        return thumbnails
    
    def upload_image(
        self, 
        file: UploadFile, 
        category: str = "products",
        create_thumbnails: bool = True
    ) -> Dict[str, Any]:
        """
        Upload image with shop isolation
        
        Args:
            file: Uploaded file
            category: Category (products, categories, users)
            create_thumbnails: Whether to create different sizes
            
        Returns:
            Dict with image URLs and metadata
        """
        # Validate file
        self._validate_file(file)
        
        # Validate category
        if category not in ['products', 'categories', 'users']:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category: {category}. Must be 'products', 'categories', or 'users'"
            )
        
        # Generate unique filename
        filename = self._generate_filename(file.filename)
        filename_base = Path(filename).stem
        
        # Create file path
        file_path = self.base_path / category / filename
        
        # Save original file
        self._save_file(file, file_path)
        
        # Create response
        result = {
            "shop": self.shop,
            "category": category,
            "filename": filename,
            "original_url": f"{self.base_url}/{category}/{filename}",
            "file_size": os.path.getsize(file_path),
            "content_type": file.content_type,
            "thumbnails": {}
        }
        
        # Create thumbnails if requested
        if create_thumbnails:
            try:
                thumbnails = self._create_thumbnails(file_path, category, filename_base)
                result["thumbnails"] = thumbnails
            except Exception as e:
                print(f"Thumbnail creation failed: {str(e)}")
        
        return result
    
    def delete_image(self, filename: str, category: str = "products") -> bool:
        """Delete image and its thumbnails"""
        try:
            # Delete original file
            file_path = self.base_path / category / filename
            if file_path.exists():
                file_path.unlink()
            
            # Delete thumbnails
            filename_base = Path(filename).stem
            for size_name in self.IMAGE_SIZES.keys():
                thumb_filename = f"{filename_base}_{size_name}.jpg"
                thumb_path = self.base_path / category / thumb_filename
                if thumb_path.exists():
                    thumb_path.unlink()
            
            return True
        except Exception as e:
            print(f"Error deleting image: {str(e)}")
            return False
    
    def list_images(self, category: str = "products") -> List[Dict[str, Any]]:
        """List all images in a category"""
        try:
            category_path = self.base_path / category
            if not category_path.exists():
                return []
            
            images = []
            for file_path in category_path.glob("*"):
                if file_path.is_file() and not file_path.name.endswith(('_thumbnail.jpg', '_small.jpg', '_medium.jpg', '_large.jpg')):
                    file_stats = file_path.stat()
                    images.append({
                        "filename": file_path.name,
                        "url": f"{self.base_url}/{category}/{file_path.name}",
                        "size": file_stats.st_size,
                        "created": file_stats.st_ctime
                    })
            
            return sorted(images, key=lambda x: x['created'], reverse=True)
        except Exception as e:
            print(f"Error listing images: {str(e)}")
            return []
    
    def get_image_info(self, filename: str, category: str = "products") -> Optional[Dict[str, Any]]:
        """Get information about specific image"""
        try:
            file_path = self.base_path / category / filename
            if not file_path.exists():
                return None
            
            file_stats = file_path.stat()
            filename_base = Path(filename).stem
            
            # Check for thumbnails
            thumbnails = {}
            for size_name in self.IMAGE_SIZES.keys():
                thumb_filename = f"{filename_base}_{size_name}.jpg"
                thumb_path = self.base_path / category / thumb_filename
                if thumb_path.exists():
                    thumbnails[size_name] = f"{self.base_url}/{category}/{thumb_filename}"
            
            return {
                "shop": self.shop,
                "category": category,
                "filename": filename,
                "url": f"{self.base_url}/{category}/{filename}",
                "size": file_stats.st_size,
                "created": file_stats.st_ctime,
                "modified": file_stats.st_mtime,
                "thumbnails": thumbnails
            }
        except Exception as e:
            print(f"Error getting image info: {str(e)}")
            return None

# Utility functions
def get_image_service(shop: str) -> ImageService:
    """Factory function to get ImageService for specific shop"""
    return ImageService(shop)

def validate_shop(shop: str) -> str:
    """Validate and return shop name"""
    if shop not in ['tinashop', 'micocah', 'shared']:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid shop: {shop}. Must be 'tinashop', 'micocah', or 'shared'"
        )
    return shop
