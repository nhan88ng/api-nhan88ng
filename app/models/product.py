from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    category: str
    stock_quantity: int = 0
    images: List[str] = []
    is_active: bool = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    name: Optional[str] = None
    price: Optional[Decimal] = None
    category: Optional[str] = None

class ProductInDB(ProductBase):
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime

class Product(ProductInDB):
    pass
