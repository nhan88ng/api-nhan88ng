"""
Product API Routes
FastAPI endpoints for product management
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path

from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse, ProductSearchQuery,
    CategoryCreate, CategoryUpdate, CategoryResponse, InventoryUpdate
)
from app.crud.product import product_crud
from app.core.deps import get_current_user, get_current_user_optional, require_role
from app.core.permissions import UserRole

router = APIRouter()

# PRODUCT ENDPOINTS

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    current_user: dict = Depends(require_role(UserRole.ADMIN))
):
    """
    Create a new product
    
    **Admin access required**
    """
    try:
        shop = current_user.get("shop", "tinashop")  # Default to tinashop
        user_id = current_user.get("sub") or current_user.get("id", "unknown")
        
        result = product_crud.create_product(product, created_by=user_id)
        return ProductResponse(**result)
    except ValueError as e:
        print(f"Product creation ValueError: {e}")  # Debug log
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"Product creation Exception: {e}")  # Debug log
        import traceback
        traceback.print_exc()  # Debug stack trace
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create product"
        )

async def get_current_user_optional():
    """Get current user if authenticated, otherwise None"""
    try:
        from fastapi.security import HTTPAuthorizationCredentials
        from fastapi import Request
        # Try to get user, return None if not authenticated
        return None  # For now, make it work without auth
    except:
        return None

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str = Path(..., description="Product ID"),
    shop: str = Query(default="tinashop", description="Shop name"),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Get product by ID
    
    **Authentication optional**
    """
    try:
        product = product_crud.get_product_by_id(product_id, shop)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        return ProductResponse(**product)
    except ValueError as e:
        # Invalid ObjectId format should also return 404 for better UX
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving product"
        )

@router.get("/slug/{slug}", response_model=ProductResponse)
async def get_product_by_slug(
    slug: str = Path(..., description="Product slug"),
    shop: str = Query(default="tinashop", description="Shop name"),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Get product by slug (SEO-friendly URL)
    
    **Authentication optional**
    """
    try:
        product = product_crud.get_product_by_slug(slug, shop)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        return ProductResponse(**product)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid slug format: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving product"
        )

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    product_update: ProductUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a product by ID"""
    shop = current_user.get("shop", "tinashop")  # Default to tinashop
    result = product_crud.update_product(product_id, product_update, shop)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return result

@router.delete("/{product_id}")
async def delete_product(
    product_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete product (soft delete)
    
    **Admin access required**
    """
    shop = current_user.get("shop", "tinashop")  # Default to tinashop
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
    sort_order: str = Query("desc", description="Sort order"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size")
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
    current_user: dict = Depends(get_current_user)
):
    """
    Update product inventory
    
    **Admin access required**
    """
    try:
        result = product_crud.update_inventory(
            product_id, shop, inventory_update, current_user["id"]
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
    current_user: dict = Depends(get_current_user)
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
    parent_id: Optional[str] = Query(None, description="Parent category ID")
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
    shop: str = Query(default="tinashop", description="Shop name")
):
    """
    Get category by ID
    
    **Authentication optional**
    """
    try:
        category = product_crud.get_category_by_id(category_id, shop)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        return CategoryResponse(**category)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid category ID format: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving category"
        )

@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: str = Path(..., description="Category ID"),
    category_update: CategoryUpdate = None,
    shop: str = Query(..., description="Shop name"),
    current_user: dict = Depends(get_current_user)
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
    current_user: dict = Depends(get_current_user)
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
    shop: str = Query(default="tinashop", description="Shop name"),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Get product statistics overview
    
    **Authentication optional for basic stats**
    """
    try:
        from app.db.database import get_database
        db = get_database(shop)
        products_collection = db["products"]
        categories_collection = db["categories"]
        
        # Basic counts (available to all)
        total_products = products_collection.count_documents({"shop": shop})
        total_categories = categories_collection.count_documents({"shop": shop})
        
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
        
        basic_stats = {
            "total_products": total_products,
            "total_categories": total_categories,
            "low_stock_count": low_stock,
            "out_of_stock_count": out_of_stock,
            "shop": shop
        }
        
        # Detailed stats only for authenticated users
        if current_user:
            # Products by status
            status_counts = {}
            status_pipeline = [
                {"$match": {"shop": shop}},
                {"$group": {"_id": "$status", "count": {"$sum": 1}}}
            ]
            for result in products_collection.aggregate(status_pipeline):
                status_counts[result["_id"] or "active"] = result["count"]
            
            # Featured products
            featured_count = products_collection.count_documents({
                "shop": shop,
                "is_featured": True
            })
            
            basic_stats.update({
                "status_counts": status_counts,
                "featured_count": featured_count
            })
        
        return basic_stats
        
    except Exception as e:
        print(f"Stats error: {e}")  # Debug log
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch product statistics"
        )
