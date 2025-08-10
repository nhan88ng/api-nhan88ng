"""
Product CRUD Operations
Database operations for products and categories
"""

from typing import List, Optional, Dict, Any
from bson import ObjectId
from pymongo.collection import Collection
from pymongo import ASCENDING, DESCENDING
from datetime import datetime
import re

from app.db.database import get_database
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse, ProductCategory,
    CategoryCreate, CategoryUpdate, CategoryResponse, ProductSearchQuery,
    InventoryUpdate, InventoryHistory, ProductStatus
)

class ProductCRUD:
    """Product CRUD operations"""
    
    def __init__(self):
        self.products_collection = None
        self.categories_collection = None
        self.inventory_history_collection = None
    
    def _get_collections(self, shop: str):
        """Get collections for the specified shop"""
        db = get_database(shop)
        self.products_collection = db["products"]
        self.categories_collection = db["categories"]
        self.inventory_history_collection = db["inventory_history"]
        
        # Create indexes if they don't exist
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Ensure required indexes exist"""
        if self.products_collection is not None:
            # Product indexes
            self.products_collection.create_index("sku", unique=True)
            self.products_collection.create_index("slug", unique=True)
            self.products_collection.create_index("shop")
            self.products_collection.create_index("status")
            self.products_collection.create_index("category_ids")
            self.products_collection.create_index("tags")
            self.products_collection.create_index("price")
            self.products_collection.create_index("created_at")
            self.products_collection.create_index([("name", "text"), ("description", "text"), ("tags", "text")])
        
        if self.categories_collection is not None:
            # Category indexes
            self.categories_collection.create_index("slug", unique=True)
            self.categories_collection.create_index("shop")
            self.categories_collection.create_index("parent_id")
    
    def _generate_slug(self, name: str, collection: Collection, exclude_id: str = None) -> str:
        """Generate unique slug from name"""
        base_slug = re.sub(r'[^\w\s-]', '', name.lower())
        base_slug = re.sub(r'[-\s]+', '-', base_slug).strip('-')
        
        slug = base_slug
        counter = 1
        
        while True:
            query = {"slug": slug}
            if exclude_id:
                query["_id"] = {"$ne": ObjectId(exclude_id)}
            
            if not collection.find_one(query):
                break
            
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug
    
    # PRODUCT OPERATIONS
    
    def create_product(self, product_data: ProductCreate, created_by: str) -> Dict[str, Any]:
        """Create a new product"""
        self._get_collections(product_data.shop)
        
        # Check if SKU already exists
        if self.products_collection.find_one({"sku": product_data.sku}):
            raise ValueError(f"Product with SKU {product_data.sku} already exists")
        
        # Generate slug
        slug = self._generate_slug(product_data.name, self.products_collection)
        
        # Prepare product document
        product_doc = {
            **product_data.dict(exclude={"shop"}),
            "slug": slug,
            "shop": product_data.shop,
            "created_by": created_by,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "view_count": 0,
            "sales_count": 0
        }
        
        # Insert product
        result = self.products_collection.insert_one(product_doc)
        
        # Get created product
        product = self.products_collection.find_one({"_id": result.inserted_id})
        return self._format_product_response(product)
    
    def get_product_by_id(self, product_id: str, shop: str) -> Optional[Dict[str, Any]]:
        """Get product by ID"""
        self._get_collections(shop)
        
        try:
            # Validate ObjectId format
            if not ObjectId.is_valid(product_id):
                raise ValueError(f"Invalid ObjectId format: {product_id}")
                
            product = self.products_collection.find_one({
                "_id": ObjectId(product_id),
                "shop": shop
            })
            
            if product:
                return self._format_product_response(product)
            return None
            
        except ValueError:
            raise  # Re-raise ValueError for API handling
        except Exception as e:
            print(f"Error getting product by ID: {e}")
            return None
    
    def get_product_by_slug(self, slug: str, shop: str) -> Optional[Dict[str, Any]]:
        """Get product by slug"""
        self._get_collections(shop)
        
        product = self.products_collection.find_one({
            "slug": slug,
            "shop": shop
        })
        
        if product:
            # Increment view count
            self.products_collection.update_one(
                {"_id": product["_id"]},
                {"$inc": {"view_count": 1}}
            )
            product["view_count"] += 1
            return self._format_product_response(product)
        
        return None
    
    def update_product(self, product_id: str, update_data: ProductUpdate, shop: str) -> Optional[Dict[str, Any]]:
        """Update product"""
        self._get_collections(shop)
        
        try:
            # Check if product exists
            existing_product = self.products_collection.find_one({
                "_id": ObjectId(product_id),
                "shop": shop
            })
            
            if not existing_product:
                return None
            
            # Prepare update data
            update_dict = {k: v for k, v in update_data.dict(exclude_unset=True).items() if v is not None}
            
            if update_dict:
                # Generate new slug if name changed
                if "name" in update_dict:
                    update_dict["slug"] = self._generate_slug(
                        update_dict["name"], 
                        self.products_collection, 
                        exclude_id=product_id
                    )
                
                update_dict["updated_at"] = datetime.utcnow()
                
                # Update product
                self.products_collection.update_one(
                    {"_id": ObjectId(product_id)},
                    {"$set": update_dict}
                )
            
            # Get updated product
            updated_product = self.products_collection.find_one({"_id": ObjectId(product_id)})
            return self._format_product_response(updated_product)
            
        except Exception:
            return None
    
    def delete_product(self, product_id: str, shop: str) -> bool:
        """Delete product (soft delete by setting status to discontinued)"""
        self._get_collections(shop)
        
        try:
            result = self.products_collection.update_one(
                {"_id": ObjectId(product_id), "shop": shop},
                {
                    "$set": {
                        "status": ProductStatus.DISCONTINUED,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception:
            return False
    
    def search_products(self, search_query: ProductSearchQuery) -> Dict[str, Any]:
        """Search products with filtering and pagination"""
        self._get_collections(search_query.shop)
        
        # Build query
        query = {"shop": search_query.shop}
        
        # Text search
        if search_query.q:
            query["$text"] = {"$search": search_query.q}
        
        # Category filter
        if search_query.category_id:
            query["category_ids"] = search_query.category_id
        
        # Tags filter
        if search_query.tags:
            query["tags"] = {"$in": search_query.tags}
        
        # Price range
        if search_query.min_price is not None or search_query.max_price is not None:
            price_query = {}
            if search_query.min_price is not None:
                price_query["$gte"] = search_query.min_price
            if search_query.max_price is not None:
                price_query["$lte"] = search_query.max_price
            query["price"] = price_query
        
        # Status filter
        if search_query.status:
            query["status"] = search_query.status
        
        # Featured filter
        if search_query.is_featured is not None:
            query["is_featured"] = search_query.is_featured
        
        # In stock filter
        if search_query.in_stock is not None:
            if search_query.in_stock:
                query["stock_quantity"] = {"$gt": 0}
            else:
                query["stock_quantity"] = {"$lte": 0}
        
        # Sorting
        sort_direction = ASCENDING if search_query.sort_order == "asc" else DESCENDING
        sort_field = search_query.sort_by
        
        # Calculate pagination
        skip = (search_query.page - 1) * search_query.size
        
        # Execute query
        cursor = self.products_collection.find(query).sort(sort_field, sort_direction).skip(skip).limit(search_query.size)
        products = list(cursor)
        
        # Get total count
        total = self.products_collection.count_documents(query)
        
        # Format response
        formatted_products = [self._format_product_response(product) for product in products]
        
        pages = (total + search_query.size - 1) // search_query.size
        
        return {
            "products": formatted_products,
            "total": total,
            "page": search_query.page,
            "size": search_query.size,
            "pages": pages,
            "has_next": search_query.page < pages,
            "has_prev": search_query.page > 1
        }
    
    def update_inventory(self, product_id: str, shop: str, inventory_update: InventoryUpdate, updated_by: str) -> Optional[Dict[str, Any]]:
        """Update product inventory"""
        self._get_collections(shop)
        
        try:
            # Get current product
            product = self.products_collection.find_one({
                "_id": ObjectId(product_id),
                "shop": shop
            })
            
            if not product:
                return None
            
            current_quantity = product.get("stock_quantity", 0)
            new_quantity = current_quantity + inventory_update.quantity_change
            
            # Prevent negative inventory unless backorder is allowed
            if new_quantity < 0 and not product.get("allow_backorder", False):
                raise ValueError("Insufficient inventory")
            
            # Update product inventory
            self.products_collection.update_one(
                {"_id": ObjectId(product_id)},
                {
                    "$set": {
                        "stock_quantity": new_quantity,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Record inventory history
            history_doc = {
                "product_id": product_id,
                "quantity_before": current_quantity,
                "quantity_change": inventory_update.quantity_change,
                "quantity_after": new_quantity,
                "reason": inventory_update.reason,
                "notes": inventory_update.notes,
                "created_by": updated_by,
                "created_at": datetime.utcnow()
            }
            
            self.inventory_history_collection.insert_one(history_doc)
            
            # Get updated product
            updated_product = self.products_collection.find_one({"_id": ObjectId(product_id)})
            return self._format_product_response(updated_product)
            
        except Exception as e:
            raise ValueError(str(e))
    
    # CATEGORY OPERATIONS
    
    def create_category(self, category_data: CategoryCreate) -> Dict[str, Any]:
        """Create a new category"""
        self._get_collections(category_data.shop)
        
        # Generate slug if not provided
        if not category_data.slug:
            slug = self._generate_slug(category_data.name, self.categories_collection)
        else:
            # Check if slug already exists
            if self.categories_collection.find_one({"slug": category_data.slug}):
                raise ValueError(f"Category with slug {category_data.slug} already exists")
            slug = category_data.slug
        
        # Prepare category document
        category_doc = {
            **category_data.dict(exclude={"shop", "slug"}),
            "slug": slug,
            "shop": category_data.shop,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert category
        result = self.categories_collection.insert_one(category_doc)
        
        # Get created category
        category = self.categories_collection.find_one({"_id": result.inserted_id})
        return self._format_category_response(category)
    
    def get_categories(self, shop: str, parent_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get categories"""
        self._get_collections(shop)
        
        query = {"shop": shop}
        if parent_id:
            query["parent_id"] = parent_id
        elif parent_id is None:
            query["parent_id"] = {"$in": [None, ""]}
        
        categories = list(self.categories_collection.find(query).sort("name", ASCENDING))
        return [self._format_category_response(category) for category in categories]
    
    def get_category_by_id(self, category_id: str, shop: str) -> Optional[Dict[str, Any]]:
        """Get category by ID"""
        self._get_collections(shop)
        
        try:
            # Validate ObjectId format
            if not ObjectId.is_valid(category_id):
                raise ValueError(f"Invalid ObjectId format: {category_id}")
                
            category = self.categories_collection.find_one({
                "_id": ObjectId(category_id),
                "shop": shop
            })
            
            if category:
                return self._format_category_response(category)
            return None
            
        except ValueError:
            raise  # Re-raise ValueError for API handling
        except Exception as e:
            print(f"Error getting category by ID: {e}")
            return None
    
    def update_category(self, category_id: str, update_data: CategoryUpdate, shop: str) -> Optional[Dict[str, Any]]:
        """Update category"""
        self._get_collections(shop)
        
        try:
            # Check if category exists
            existing_category = self.categories_collection.find_one({
                "_id": ObjectId(category_id),
                "shop": shop
            })
            
            if not existing_category:
                return None
            
            # Prepare update data
            update_dict = {k: v for k, v in update_data.dict(exclude_unset=True).items() if v is not None}
            
            if update_dict:
                # Generate new slug if name changed
                if "name" in update_dict and "slug" not in update_dict:
                    update_dict["slug"] = self._generate_slug(
                        update_dict["name"], 
                        self.categories_collection, 
                        exclude_id=category_id
                    )
                
                update_dict["updated_at"] = datetime.utcnow()
                
                # Update category
                self.categories_collection.update_one(
                    {"_id": ObjectId(category_id)},
                    {"$set": update_dict}
                )
            
            # Get updated category
            updated_category = self.categories_collection.find_one({"_id": ObjectId(category_id)})
            return self._format_category_response(updated_category)
            
        except Exception:
            return None
    
    def delete_category(self, category_id: str, shop: str) -> bool:
        """Delete category"""
        self._get_collections(shop)
        
        try:
            # Check if category has products
            product_count = self.products_collection.count_documents({
                "category_ids": category_id,
                "shop": shop
            })
            
            if product_count > 0:
                raise ValueError("Cannot delete category with products")
            
            # Check if category has subcategories
            child_count = self.categories_collection.count_documents({
                "parent_id": category_id,
                "shop": shop
            })
            
            if child_count > 0:
                raise ValueError("Cannot delete category with subcategories")
            
            result = self.categories_collection.delete_one({
                "_id": ObjectId(category_id),
                "shop": shop
            })
            
            return result.deleted_count > 0
            
        except Exception as e:
            raise ValueError(str(e))
    
    # HELPER METHODS
    
    def _format_product_response(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Format product for response - FIXED: Comprehensive ObjectId conversion"""
        # Convert main product ObjectId
        if "_id" in product:
            product["id"] = str(product["_id"])
            del product["_id"]
        
        # Convert any remaining ObjectIds in product data
        product = self._convert_objectids_to_strings(product)
        
        # Get categories
        if product.get("category_ids"):
            try:
                categories = list(self.categories_collection.find({
                    "_id": {"$in": [ObjectId(cat_id) for cat_id in product["category_ids"]]}
                }))
                product["categories"] = [self._format_category_response(cat) for cat in categories]
            except Exception as e:
                print(f"Error formatting categories: {e}")
                product["categories"] = []
        else:
            product["categories"] = []
        
        return product
    
    def _convert_objectids_to_strings(self, data: Any) -> Any:
        """Recursively convert all ObjectIds to strings in a data structure"""
        if hasattr(data, 'binary'):  # It's an ObjectId
            return str(data)
        elif isinstance(data, dict):
            return {key: self._convert_objectids_to_strings(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._convert_objectids_to_strings(item) for item in data]
        else:
            return data
    
    def _format_category_response(self, category: Dict[str, Any]) -> Dict[str, Any]:
        """Format category for response - FIXED: Ensure all ObjectIds are converted"""
        # Convert main category ObjectId to string
        if "_id" in category:
            category["id"] = str(category["_id"])
            del category["_id"]
        
        # Convert any remaining ObjectIds to strings
        for key, value in category.items():
            if hasattr(value, 'binary'):  # Check if it's ObjectId
                category[key] = str(value)
        
        # Count products in this category
        category["product_count"] = self.products_collection.count_documents({
            "category_ids": category["id"],
            "shop": category["shop"]
        })
        
        # Get subcategories and recursively format them
        children = list(self.categories_collection.find({
            "parent_id": category["id"],
            "shop": category["shop"]
        }).sort("name", ASCENDING))
        
        # Recursively format children (this ensures all nested ObjectIds are converted)
        category["children"] = [self._format_category_response(child) for child in children]
        
        return category

# Create global instance
product_crud = ProductCRUD()
