from typing import Optional
import re

from pydantic import BaseModel, Field, validator


class ProductBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    sku: str = Field(..., min_length=3, max_length=50)
    category: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None, min_length=10, max_length=1000)
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    
    @validator('price')
    def price_must_be_positive_and_valid(cls, v):
        if v <= 0:
            raise ValueError('Price must be greater than zero')
        price_str = str(v)
        if '.' in price_str:
            decimal_places = len(price_str.split('.')[1])
            if decimal_places > 2:
                raise ValueError('Price can have at most 2 decimal places')
        return round(v, 2)  # Round to 2 decimal places
    
    @validator('sku')
    def sku_must_be_valid(cls, v):
        if not re.match(r'^[A-Za-z0-9\-]+$', v):
            raise ValueError('SKU must contain only letters, numbers, and hyphens')
        return v.upper()
    
    @validator('name')
    def name_must_be_valid(cls, v):
        if not re.match(r'^[A-Za-z0-9\s\.\,\-\&\(\)]+$', v):
            raise ValueError('Product name contains invalid characters')
        return v


class ProductCreate(ProductBase):
    pass


class ProductInDB(ProductBase):
    id: int
    
    class Config:
        from_attributes = True


class Product(ProductInDB):
    pass 