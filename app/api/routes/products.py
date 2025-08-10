"""
Product API Routes
FastAPI endpoints for product management
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from fastapi.security import HTTPBearer
from bson import ObjectId
from bson.errors import InvalidId

from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse, ProductSearchQuery,
    CategoryCreate, CategoryUpdate, CategoryResponse, InventoryUpdate
)
from app.crud.product import product_crud
from app.core.deps import get_current_user
from app.schemas.responses import UserResponse

router = APIRouter(prefix="/products", tags=["Products"])
security = HTTPBearer()

def validate_object_id(id_string: str, field_name: str = "ID") -> str:
    """Validate ObjectId and return proper error if invalid"""
    try:
        ObjectId(id_string)
        return id_string
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{field_name} not found"
        )

# PRODUCT ENDPOINTS

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    current_user: UserResponse = Depends(get_current_admin_user)
):
    """
    Create a new product
    
    **Admin access required**
    """
    try:
        result = product_crud.create_product(product, current_user.id)
        return ProductResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create product"
        )

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str = Path(..., description="Product ID"),
    shop: str = Query(..., description="Shop name"),
    current_user: Optional[UserResponse] = Depends(get_current_user)
):
    """
    Get product by ID
    
    **Authentication optional**
    """
    # Validate ObjectId format
    validate_object_id(product_id, "Product ID")
    
    product = product_crud.get_product_by_id(product_id, shop)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return ProductResponse(**product)

@router.get("/slug/{slug}", response_model=ProductResponse)
async def get_product_by_slug(
    slug: str = Path(..., description="Product slug"),
    shop: str = Query(..., description="Shop name"),
    current_user: Optional[UserResponse] = Depends(get_current_user)
):
    """
    Get product by slug (SEO-friendly URL)
    
    **Authentication optional**
    """
    product = product_crud.get_product_by_slug(slug, shop)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return ProductResponse(**product)

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str = Path(..., description="Product ID"),
    product_update: ProductUpdate = None,
    shop: str = Query(..., description="Shop name"),
    current_user: UserResponse = Depends(get_current_admin_user)
):
    """
    Update product (Admin only)
    
    **Requires admin authentication**
    """
    # Validate ObjectId format
    validate_object_id(product_id, "Product ID")
    
    # Get existing product
    existing_product = product_crud.get_product_by_id(product_id, shop)
    if not existing_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

@router.delete("/{product_id}")
async def delete_product(
    product_id: str = Path(..., description="Product ID"),
    shop: str = Query(..., description="Shop name"),
    current_user: UserResponse = Depends(get_current_admin_user)
):
    """
    Delete product (soft delete)
    
    **Admin access required**
    """
    success = product_crud.delete_product(product_id, shop)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return {"message": "Product deleted successfully"}

@router.get("/", response_model=Dict[str, Any])
async def search_products(
    shop: str = Query(..., description="Shop name"),
    q: Optional[str] = Query(None, description="Search query"),
    category_id: Optional[str] = Query(None, description="Category ID"),
    tags: Optional[List[str]] = Query(None, description="Product tags"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    status: Optional[str] = Query(None, description="Product status"),
    is_featured: Optional[bool] = Query(None, description="Featured products only"),
    in_stock: Optional[bool] = Query(None, description="In stock products only"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    current_user: Optional[UserResponse] = Depends(get_current_user)
):
    """
    Search and filter products with pagination
    
    **Authentication optional**
    """
    search_query = ProductSearchQuery(
        shop=shop,
        q=q,
        category_id=category_id,
        tags=tags or [],
        min_price=min_price,
        max_price=max_price,
        status=status,
        is_featured=is_featured,
        in_stock=in_stock,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        size=size
    )
    
    try:
        result = product_crud.search_products(search_query)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search products"
        )

@router.patch("/{product_id}/inventory", response_model=ProductResponse)
async def update_product_inventory(
    product_id: str = Path(..., description="Product ID"),
    inventory_update: InventoryUpdate = None,
    shop: str = Query(..., description="Shop name"),
    current_user: UserResponse = Depends(get_current_admin_user)
):
    """
    Update product inventory
    
    **Admin access required**
    """
    try:
        result = product_crud.update_inventory(
            product_id, shop, inventory_update, current_user.id
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        return ProductResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update inventory"
        )

# CATEGORY ENDPOINTS

@router.post("/categories/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: CategoryCreate,
    current_user: UserResponse = Depends(get_current_admin_user)
):
    """
    Create a new category
    
    **Admin access required**
    """
    try:
        result = product_crud.create_category(category)
        return CategoryResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create category"
        )

@router.get("/categories/", response_model=List[CategoryResponse])
async def get_categories(
    shop: str = Query(..., description="Shop name"),
    parent_id: Optional[str] = Query(None, description="Parent category ID"),
    current_user: Optional[UserResponse] = Depends(get_current_user)
):
    """
    Get categories (optionally filtered by parent)
    
    **Authentication optional**
    """
    try:
        categories = product_crud.get_categories(shop, parent_id)
        return [CategoryResponse(**category) for category in categories]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch categories"
        )

@router.get("/categories/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: str = Path(..., description="Category ID"),
    shop: str = Query(..., description="Shop name"),
    current_user: Optional[UserResponse] = Depends(get_current_user)
):
    """
    Get category by ID
    
    **Authentication optional**
    """
    category = product_crud.get_category_by_id(category_id, shop)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    return CategoryResponse(**category)

@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: str = Path(..., description="Category ID"),
    category_update: CategoryUpdate = None,
    shop: str = Query(..., description="Shop name"),
    current_user: UserResponse = Depends(get_current_admin_user)
):
    """
    Update category
    
    **Admin access required**
    """
    try:
        result = product_crud.update_category(category_id, category_update, shop)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        return CategoryResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update category"
        )

@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: str = Path(..., description="Category ID"),
    shop: str = Query(..., description="Shop name"),
    current_user: UserResponse = Depends(get_current_admin_user)
):
    """
    Delete category
    
    **Admin access required**
    """
    try:
        success = product_crud.delete_category(category_id, shop)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        return {"message": "Category deleted successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete category"
        )

# STATISTICS ENDPOINTS

@router.get("/stats/overview")
async def get_product_stats(
    shop: str = Query(..., description="Shop name"),
    current_user: UserResponse = Depends(get_current_admin_user)
):
    """
    Get product statistics overview
    
    **Admin access required**
    """
    try:
        from app.db.database import get_database
        db = get_database(shop)
        products_collection = db["products"]
        categories_collection = db["categories"]
        
        # Basic counts
        total_products = products_collection.count_documents({"shop": shop})
        total_categories = categories_collection.count_documents({"shop": shop})
        
        # Products by status
        status_counts = {}
        status_pipeline = [
            {"$match": {"shop": shop}},
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        for result in products_collection.aggregate(status_pipeline):
            status_counts[result["_id"]] = result["count"]
        
        # Low stock products (< 10 items)
        low_stock = products_collection.count_documents({
            "shop": shop,
            "stock_quantity": {"$lt": 10, "$gt": 0}
        })
        
        # Out of stock products
        out_of_stock = products_collection.count_documents({
            "shop": shop,
            "stock_quantity": {"$lte": 0}
        })
        
        # Featured products
        featured_count = products_collection.count_documents({
            "shop": shop,
            "is_featured": True
        })
        
        return {
            "total_products": total_products,
            "total_categories": total_categories,
            "status_counts": status_counts,
            "low_stock_count": low_stock,
            "out_of_stock_count": out_of_stock,
            "featured_count": featured_count
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch product statistics"
        )
