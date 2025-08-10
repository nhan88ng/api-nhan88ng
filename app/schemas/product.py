"""
Product Management Schemas
Pydantic models for product-related operations
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ProductStatus(str, Enum):
    """Product status enum"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    OUT_OF_STOCK = "out_of_stock"
    DISCONTINUED = "discontinued"

class ProductCategory(BaseModel):
    """Product category schema"""
    id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    slug: str = Field(..., min_length=1, max_length=100)
    parent_id: Optional[str] = None
    is_active: bool = True
    shop: str = Field(..., min_length=1)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ProductVariant(BaseModel):
    """Product variant schema (size, color, etc.)"""
    name: str = Field(..., min_length=1, max_length=50)  # e.g., "Size", "Color"
    value: str = Field(..., min_length=1, max_length=50)  # e.g., "Large", "Red"
    price_adjustment: float = Field(default=0.0)  # Additional price for this variant
    stock_quantity: int = Field(default=0, ge=0)
    sku_suffix: Optional[str] = Field(None, max_length=20)

class ProductImage(BaseModel):
    """Product image schema"""
    url: str = Field(..., min_length=1)
    alt_text: Optional[str] = Field(None, max_length=200)
    is_primary: bool = False
    order: int = Field(default=0, ge=0)

class ProductCreate(BaseModel):
    """Schema for creating a product"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    short_description: Optional[str] = Field(None, max_length=500)
    sku: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    compare_price: Optional[float] = Field(None, gt=0)  # Original price for discounts
    cost_price: Optional[float] = Field(None, ge=0)  # Cost for profit calculation
    category_ids: List[str] = Field(default=[])
    tags: List[str] = Field(default=[])
    images: List[ProductImage] = Field(default=[])
    variants: List[ProductVariant] = Field(default=[])
    stock_quantity: int = Field(default=0, ge=0)
    track_inventory: bool = True
    allow_backorder: bool = False
    weight: Optional[float] = Field(None, gt=0)  # For shipping calculation
    dimensions: Optional[Dict[str, float]] = Field(None)  # length, width, height
    status: ProductStatus = ProductStatus.ACTIVE
    is_featured: bool = False
    meta_title: Optional[str] = Field(None, max_length=60)
    meta_description: Optional[str] = Field(None, max_length=160)
    shop: str = Field(..., min_length=1)

    @validator('compare_price')
    def validate_compare_price(cls, v, values):
        if v is not None and 'price' in values and v <= values['price']:
            raise ValueError('Compare price must be greater than regular price')
        return v

    @validator('sku')
    def validate_sku(cls, v):
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('SKU can only contain letters, numbers, hyphens, and underscores')
        return v.upper()

class ProductUpdate(BaseModel):
    """Schema for updating a product"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    short_description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, gt=0)
    compare_price: Optional[float] = Field(None, gt=0)
    cost_price: Optional[float] = Field(None, ge=0)
    category_ids: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    images: Optional[List[ProductImage]] = None
    variants: Optional[List[ProductVariant]] = None
    stock_quantity: Optional[int] = Field(None, ge=0)
    track_inventory: Optional[bool] = None
    allow_backorder: Optional[bool] = None
    weight: Optional[float] = Field(None, gt=0)
    dimensions: Optional[Dict[str, float]] = None
    status: Optional[ProductStatus] = None
    is_featured: Optional[bool] = None
    meta_title: Optional[str] = Field(None, max_length=60)
    meta_description: Optional[str] = Field(None, max_length=160)

class ProductResponse(BaseModel):
    """Schema for product response"""
    id: str
    name: str
    description: Optional[str]
    short_description: Optional[str]
    slug: str
    sku: str
    price: float
    compare_price: Optional[float]
    cost_price: Optional[float]
    category_ids: List[str]
    categories: List[ProductCategory] = Field(default=[])  # Populated categories
    tags: List[str]
    images: List[ProductImage]
    variants: List[ProductVariant]
    stock_quantity: int
    track_inventory: bool
    allow_backorder: bool
    weight: Optional[float]
    dimensions: Optional[Dict[str, float]]
    status: ProductStatus
    is_featured: bool
    meta_title: Optional[str]
    meta_description: Optional[str]
    shop: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    view_count: int = 0
    sales_count: int = 0

class ProductListResponse(BaseModel):
    """Schema for product list response"""
    products: List[ProductResponse]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool

class CategoryCreate(BaseModel):
    """Schema for creating a category"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    parent_id: Optional[str] = None
    is_active: bool = True
    shop: str = Field(..., min_length=1)

    @validator('slug', always=True)
    def generate_slug(cls, v, values):
        if v is None and 'name' in values:
            # Generate slug from name
            import re
            slug = re.sub(r'[^\w\s-]', '', values['name'].lower())
            slug = re.sub(r'[-\s]+', '-', slug)
            return slug.strip('-')
        return v

class CategoryUpdate(BaseModel):
    """Schema for updating a category"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    parent_id: Optional[str] = None
    is_active: Optional[bool] = None

class CategoryResponse(BaseModel):
    """Schema for category response"""
    id: str
    name: str
    description: Optional[str]
    slug: str
    parent_id: Optional[str]
    is_active: bool
    shop: str
    product_count: int = 0
    children: List['CategoryResponse'] = Field(default=[])
    created_at: datetime
    updated_at: datetime

class ProductSearchQuery(BaseModel):
    """Schema for product search"""
    q: Optional[str] = Field(None, max_length=200)  # Search query
    category_id: Optional[str] = None
    tags: Optional[List[str]] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    status: Optional[ProductStatus] = None
    is_featured: Optional[bool] = None
    in_stock: Optional[bool] = None
    sort_by: Optional[str] = Field(default="created_at", pattern="^(name|price|created_at|updated_at|sales_count|view_count)$")
    sort_order: Optional[str] = Field(default="desc", pattern="^(asc|desc)$")
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)
    shop: str = Field(..., min_length=1)

    @validator('max_price')
    def validate_price_range(cls, v, values):
        if v is not None and 'min_price' in values and values['min_price'] is not None:
            if v <= values['min_price']:
                raise ValueError('Max price must be greater than min price')
        return v

class InventoryUpdate(BaseModel):
    """Schema for inventory updates"""
    quantity_change: int = Field(..., description="Positive for increase, negative for decrease")
    reason: str = Field(..., min_length=1, max_length=200)
    notes: Optional[str] = Field(None, max_length=500)

class InventoryHistory(BaseModel):
    """Schema for inventory history"""
    id: str
    product_id: str
    quantity_before: int
    quantity_change: int
    quantity_after: int
    reason: str
    notes: Optional[str]
    created_by: str
    created_at: datetime

# Update forward references
CategoryResponse.update_forward_refs()
